import json
import shutil
import cv2
from collections import Counter
from collections import deque
import time
from flask import Flask, Response, request
from flask_socketio import SocketIO, emit
from ultralytics import YOLO
from utils.Fun import Fun
from utils import predictImg, chatApi, predictBatch


# Flask 应用设置
class VideoProcessingApp:
    def __init__(self, host='0.0.0.0', port=5000):
        """初始化 Flask 应用并设置路由"""
        self.app = Flask(__name__)
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")  # 初始化 SocketIO
        self.host = host
        self.port = port
        self.fun = Fun()
        self.setup_routes()
        self.DeepSeek = 'sk-5c832673956a47cfa43af19b64aa2508'
        self.Qwen = 'sk-cxnqlvtvddxtmuyqykqhlfyyqlpwiupvnbzfqbxtlzovfuph'
        self.data = {}  # 存储接收参数
        self.paths = {
            'download': './runs/video/download.mp4',
            'output': './runs/video/output.mp4',
            'camera_output': "./runs/video/camera_output.avi",
            'video_output': "./runs/video/camera_output.avi"
        }
        self.recording = False  # 标志位，判断是否正在录制视频

    @staticmethod
    def _normalize_label(label: str) -> str:
        """统一去除标签后缀，便于统计同类行为"""
        if not isinstance(label, str):
            return str(label)
        return label.split("-")[0].strip()

    def _update_behavior_stats(self, result, behavior_counter: Counter, frame_box_total: dict) -> None:
        """从单帧推理结果中累计行为统计"""
        boxes = result.boxes
        if boxes is None or boxes.cls is None:
            return
        class_ids = boxes.cls.tolist()
        frame_box_total["count"] += len(class_ids)
        for cls_id in class_ids:
            cls_index = int(cls_id)
            raw_label = result.names.get(cls_index, str(cls_index))
            normalized_label = self._normalize_label(raw_label)
            behavior_counter[normalized_label] += 1

    @staticmethod
    def _build_behavior_summary(behavior_counter: Counter, total_boxes: int, prefix_text: str) -> str:
        """构建结构化行为摘要文本"""
        if total_boxes <= 0 or not behavior_counter:
            return f"{prefix_text} 未检测到有效行为目标。"
        top_behaviors = behavior_counter.most_common(3)
        parts = []
        for name, count in top_behaviors:
            ratio = (count / total_boxes) * 100
            parts.append(f"{name}({count}次, {ratio:.1f}%)")
        return f"{prefix_text} 共检测到{total_boxes}个目标，Top行为：{'；'.join(parts)}。"

    def _get_abnormal_count(self, labels):
        """统计单帧中的异常行为数量"""
        abnormal_keywords = {"转头", "站立", "小组讨论", "交头接耳", "离座", "打瞌睡", "玩手机"}
        abnormal_count = 0
        for label in labels:
            normalized = self._normalize_label(label)
            if any(keyword in normalized for keyword in abnormal_keywords):
                abnormal_count += 1
        return abnormal_count

    def _generate_ai_suggestion(self, ai_name: str, summary_text: str):
        """根据结构化摘要生成 AI 建议"""
        if ai_name not in {"DeepSeek", "Qwen"}:
            return "未选择AI，无AI分析！"
        prompt = (
            "我使用yolo对学生课堂行为进行检测。"
            "下面是本次视频检测的结构化摘要，请基于该结果给出课堂管理建议与优化动作，"
            "输出简洁、可执行。摘要如下："
            f"{summary_text}"
        )
        try:
            chat = chatApi.ChatAPI(
                deepseek_api_key=self.DeepSeek,
                qwen_api_key=self.Qwen
            )
            if ai_name == "DeepSeek":
                self.socketio.emit('message', {'data': '已检测完成，正在生成DeepSeekAI分析！'})
                return chat.deepseek_request(
                    [{"role": "system", "content": "You are a helpful assistant"},
                     {"role": "user", "content": prompt}]
                )
            self.socketio.emit('message', {'data': '已检测完成，正在生成QwenAI分析！'})
            return chat.qwen_request([{"role": "user", "content": prompt}])
        except Exception as exc:
            return f"AI建议生成失败：{exc}"

    @staticmethod
    def _trim_text(text: str, max_len: int = 240) -> str:
        """裁剪文本长度，避免数据库字段超长导致入库失败"""
        if text is None:
            return ""
        return text if len(text) <= max_len else text[:max_len] + "..."

    def setup_routes(self):
        """设置所有路由"""
        self.app.add_url_rule('/file_names', 'file_names', self.file_names, methods=['GET'])
        self.app.add_url_rule('/predictImgBatch', 'predictImgBatch', self.predictImgBatch, methods=['POST'])
        self.app.add_url_rule('/predictImg', 'predictImg', self.predictImg, methods=['POST'])
        self.app.add_url_rule('/predictVideo', 'predictVideo', self.predictVideo)
        self.app.add_url_rule('/predictCamera', 'predictCamera', self.predictCamera)
        self.app.add_url_rule('/stopCamera', 'stopCamera', self.stopCamera, methods=['GET'])

        # 添加 WebSocket 事件
        @self.socketio.on('connect')
        def handle_connect():
            print("WebSocket connected!")
            emit('message', {'data': 'Connected to WebSocket server!'})

        @self.socketio.on('disconnect')
        def handle_disconnect():
            print("WebSocket disconnected!")

    def run(self):
        """启动 Flask 应用"""
        self.socketio.run(self.app, host=self.host, port=self.port, allow_unsafe_werkzeug=True)

    def predictImgBatch(self):
        """图片预测接口"""
        data = request.get_json()
        self.data.clear()
        self.data.update({
            "imgFolderUrl": data['imgFolderUrl'], "username": data['username'],
            "weight": data['weight'], "conf": data['conf']
        })
        self.fun.download_folder(self.data["imgFolderUrl"], './runs/imgBatch')

        predictor = predictBatch.ImagePredictor(
            weights_path="./weights/" + self.data["weight"],
            input_folder="./runs/imgBatch",
            output_folder="./runs/resultBatch",
            conf=float(self.data["conf"]),
            data=self.data
        )
        batch_result = predictor.predict_batch()
        print(batch_result)
        shutil.rmtree("./runs/imgBatch")
        shutil.rmtree("./runs/resultBatch")
        data = {"code": 0, "message": "预测成功", "data": batch_result}

        return data

    def file_names(self):
        """模型列表接口"""
        weight_items = [{'value': name, 'label': name} for name in self.fun.get_file_names("./weights")]
        return json.dumps({'weight_items': weight_items})

    def predictImg(self):
        """图片预测接口"""
        data = request.get_json()
        self.data.clear()
        self.data.update({
            "username": data['username'], "weight": data['weight'],
            "conf": data['conf'], "startTime": data['startTime'],
            "inputImg": data['inputImg'], "ai": data['ai']
        })
        predict = predictImg.ImagePredictor(weights_path=f'./weights/{self.data["weight"]}',
                                            img_path=self.data["inputImg"], save_path='./runs/result.jpg',
                                            conf=float(self.data["conf"]))
        # 执行预测
        results = predict.predict()
        uploadedUrl = self.fun.upload('./runs/result.jpg')
        if results['labels'] != '预测失败':
            self.data["status"] = 200
            self.data["message"] = "预测成功"
            self.data["outImg"] = uploadedUrl
            self.data["allTime"] = results['allTime']
            self.data["confidence"] = json.dumps(results['confidences'])
            self.data["label"] = json.dumps(results['labels'])
        else:
            self.data["status"] = 400
            self.data["message"] = "该图片无法识别，请重新上传！"
        if self.data["ai"] == 'DeepSeek' and self.data["status"] == 200:
            self.socketio.emit('message', {'data': '已检测完成，正在生成DeepSeekAI分析！'})
            chat = chatApi.ChatAPI(
                deepseek_api_key=self.DeepSeek,
                qwen_api_key=self.Qwen
            )
            list_input = self.fun.process_list(results['labels'])
            text = ("我使用yolo对学生课堂行为进行检测。接下来我会告诉你检测到了哪些目标。"
                    "请根据检测到的学生课堂行为，进行分析和给出相关建议以实现高效课堂。只需回答我要的结果。这是我检测到的结果：")
            for i in list_input:
                text += i
                text += "，"
            messages = [
                {"role": "user",
                 "content": text}
            ]
            self.data["suggestion"] = chat.deepseek_request([{"role": "system", "content": "You are a helpful assistant"}] + messages)
        elif self.data["ai"] == 'Qwen' and self.data["status"] == 200:
            self.socketio.emit('message', {'data': '已检测完成，正在生成QwenAI分析！'})
            chat = chatApi.ChatAPI(
                deepseek_api_key=self.DeepSeek,
                qwen_api_key=self.Qwen
            )
            list_input = self.fun.process_list(results['labels'])
            text = ("我使用yolo对学生课堂行为进行检测。接下来我会告诉你检测到了哪些目标。"
                    "请根据检测到的学生课堂行为，进行分析和给出相关建议以实现高效课堂。只需回答我要的结果。这是我检测到的结果：")
            for i in list_input:
                text += i
                text += "，"
            messages = [
                {"role": "user",
                 "content": text}
            ]
            self.data["suggestion"] = chat.qwen_request(messages)
        else:
            self.data["suggestion"] = '未选择AI，无AI分析！'
        self.fun.cleanup_files(['./' + self.data["inputImg"].split('/')[-1]])
        return json.dumps(self.data, ensure_ascii=False)

    def predictVideo(self):
        """视频流处理接口"""
        self.data.clear()
        self.data.update({
            "username": request.args.get('username'), "weight": request.args.get('weight'),
            "conf": request.args.get('conf'), "startTime": request.args.get('startTime'),
            "inputVideo": request.args.get('inputVideo'),
            "ai": request.args.get('ai', '')
        })
        self.data["kind"] = "视频行为检测已完成，请结合右侧处理后视频查看目标识别结果。"
        self.fun.download(self.data["inputVideo"], self.paths['download'])
        cap = cv2.VideoCapture(self.paths['download'])
        if not cap.isOpened():
            raise ValueError("无法打开视频文件")
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        print(fps)

        # 视频写入器
        video_writer = cv2.VideoWriter(
            self.paths['video_output'],
            cv2.VideoWriter_fourcc(*'XVID'),
            fps,
            (640, 480)
        )
        model = YOLO(f'./weights/{self.data["weight"]}')
        behavior_counter = Counter()
        frame_box_total = {"count": 0}

        def generate():
            try:
                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        break
                    frame = cv2.resize(frame, (640, 480))
                    results = model.predict(source=frame, conf=float(self.data['conf']), show=False)
                    processed_frame = results[0].plot()
                    self._update_behavior_stats(results[0], behavior_counter, frame_box_total)
                    video_writer.write(processed_frame)
                    _, jpeg = cv2.imencode('.jpg', processed_frame)
                    yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n'
            finally:
                self.fun.cleanup_resources(cap, video_writer)
                self.socketio.emit('message', {'data': '处理完成，正在保存！'})
                for progress in self.fun.convert_avi_to_mp4(self.paths['video_output']):
                    self.socketio.emit('progress', {'data': progress})
                uploadedUrl = self.fun.upload(self.paths['output'])
                self.data["outVideo"] = uploadedUrl
                self.data["kind"] = self._build_behavior_summary(
                    behavior_counter,
                    frame_box_total["count"],
                    "视频行为检测已完成。"
                )
                ai_suggestion = self._generate_ai_suggestion(self.data.get("ai"), self.data["kind"])
                if ai_suggestion and ai_suggestion != "未选择AI，无AI分析！":
                    # kind 字段数据库长度有限，仅保存简版建议，完整建议通过 websocket 告知前端
                    short_ai = self._trim_text(ai_suggestion, 120)
                    self.data["kind"] = self._trim_text(f"{self.data['kind']} AI建议：{short_ai}", 240)
                video_record_payload = {
                    "username": self.data.get("username"),
                    "weight": self.data.get("weight"),
                    "conf": self.data.get("conf"),
                    "startTime": self.data.get("startTime"),
                    "inputVideo": self.data.get("inputVideo"),
                    "outVideo": self.data.get("outVideo"),
                    "kind": self.data.get("kind"),
                }
                self.fun.save_data(json.dumps(video_record_payload), 'http://localhost:9999/videoRecords')
                self.socketio.emit('video_result', {
                    'data': {
                        "outVideo": self.data.get("outVideo"),
                        "kind": self.data.get("kind"),
                        "aiSuggestion": ai_suggestion if ai_suggestion != "未选择AI，无AI分析！" else ""
                    }
                })
                self.fun.cleanup_files([self.paths['download'], self.paths['output'], self.paths['video_output']])

        return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

    def predictCamera(self):
        """摄像头视频流处理接口"""
        self.data.clear()
        self.data.update({
            "username": request.args.get('username'), "weight": request.args.get('weight'),
            "conf": request.args.get('conf'), "startTime": request.args.get('startTime'),
            "ai": request.args.get('ai', '')
        })
        self.data["kind"] = "摄像头行为检测已完成，请结合处理后视频查看目标识别结果。"
        self.socketio.emit('message', {'data': '正在加载，请稍等！'})
        model = YOLO(f'./weights/{self.data["weight"]}')
        behavior_counter = Counter()
        frame_box_total = {"count": 0}
        alert_window = deque(maxlen=60)  # 约3秒窗口（20fps）
        last_alert_ts = 0.0
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        video_writer = cv2.VideoWriter(self.paths['camera_output'], cv2.VideoWriter_fourcc(*'XVID'), 20, (640, 480))
        self.recording = True

        def generate():
            try:
                while self.recording:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    results = model.predict(source=frame, imgsz=640, conf=float(self.data['conf']), show=False)
                    processed_frame = results[0].plot()
                    self._update_behavior_stats(results[0], behavior_counter, frame_box_total)
                    frame_labels = [
                        results[0].names.get(int(cls_id), str(int(cls_id)))
                        for cls_id in (results[0].boxes.cls.tolist() if results[0].boxes is not None and results[0].boxes.cls is not None else [])
                    ]
                    frame_total = len(frame_labels)
                    frame_abnormal = self._get_abnormal_count(frame_labels)
                    alert_window.append((frame_abnormal, frame_total))
                    window_abnormal = sum(item[0] for item in alert_window)
                    window_total = sum(item[1] for item in alert_window)
                    abnormal_ratio = (window_abnormal / window_total) if window_total > 0 else 0
                    now_ts = time.time()
                    if window_total >= 12 and abnormal_ratio >= 0.35 and (now_ts - last_alert_ts) >= 8:
                        self.socketio.emit('alert', {
                            'data': {
                                'level': 'warning',
                                'ratio': round(abnormal_ratio * 100, 1),
                                'message': f'检测到异常行为占比升高（{abnormal_ratio * 100:.1f}%），建议教师关注当前课堂状态。'
                            }
                        })
                        last_alert_ts = now_ts
                    if self.recording and video_writer:
                        video_writer.write(processed_frame)
                    _, jpeg = cv2.imencode('.jpg', processed_frame)
                    yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n'
            finally:
                self.fun.cleanup_resources(cap, video_writer)
                self.socketio.emit('message', {'data': '处理完成，正在保存！'})
                for progress in self.fun.convert_avi_to_mp4(self.paths['camera_output']):
                    self.socketio.emit('progress', {'data': progress})
                uploadedUrl = self.fun.upload(self.paths['output'])
                self.data["outVideo"] = uploadedUrl
                self.data["kind"] = self._build_behavior_summary(
                    behavior_counter,
                    frame_box_total["count"],
                    "摄像头行为检测已完成。"
                )
                ai_suggestion = self._generate_ai_suggestion(self.data.get("ai"), self.data["kind"])
                if ai_suggestion and ai_suggestion != "未选择AI，无AI分析！":
                    short_ai = self._trim_text(ai_suggestion, 120)
                    self.data["kind"] = self._trim_text(f"{self.data['kind']} AI建议：{short_ai}", 240)
                camera_record_payload = {
                    "username": self.data.get("username"),
                    "weight": self.data.get("weight"),
                    "conf": self.data.get("conf"),
                    "startTime": self.data.get("startTime"),
                    "outVideo": self.data.get("outVideo"),
                    "kind": self.data.get("kind"),
                }
                self.fun.save_data(json.dumps(camera_record_payload), 'http://localhost:9999/cameraRecords')
                self.socketio.emit('camera_result', {
                    'data': {
                        "outVideo": self.data.get("outVideo"),
                        "kind": self.data.get("kind"),
                        "aiSuggestion": ai_suggestion if ai_suggestion != "未选择AI，无AI分析！" else ""
                    }
                })
                self.fun.cleanup_files([self.paths['download'], self.paths['output'], self.paths['camera_output']])

        return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

    def stopCamera(self):
        """停止摄像头预测"""
        self.recording = False
        return json.dumps({"status": 200, "message": "预测成功", "code": 0})


# 启动应用
if __name__ == '__main__':
    video_app = VideoProcessingApp()
    video_app.run()
