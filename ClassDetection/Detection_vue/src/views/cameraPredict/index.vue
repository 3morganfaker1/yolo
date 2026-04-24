<template>
	<div class="system-predict-container layout-padding">
		<div class="system-predict-padding layout-padding-auto layout-padding-view">
			<div class="header">
				<div class="weight">
					<el-select v-model="weight" placeholder="请选择模型" size="large" style="width: 200px">
						<el-option v-for="item in state.weight_items" :key="item.value" :label="item.label"
							:value="item.value" />
					</el-select>
				</div>
				<div class="conf" style="margin-left: 20px;display: flex; flex-direction: row;">
					<div
						style="font-size: 14px;margin-right: 20px;display: flex;justify-content: start;align-items: center;color: #909399;">
						设置最小置信度阈值</div>
					<el-slider v-model="conf" :format-tooltip="formatTooltip" style="width: 300px;" />
				</div>
				<div class="ai" style="margin-left: 20px">
					<el-select v-model="state.form.ai" placeholder="选择AI助手" size="large" style="width: 160px">
						<el-option label="不使用AI" value="" />
						<el-option label="DeepSeek" value="DeepSeek" />
						<el-option label="Qwen" value="Qwen" />
					</el-select>
				</div>
				<div class="button-section" style="margin-left: 20px">
					<el-button type="primary" @click="startRecording" :disabled="state.isRecording" class="predict-button">开始录制</el-button>
				</div>
				<div class="button-section" style="margin-left: 20px">
					<el-button type="warning" @click="stopRecording" :disabled="!state.isRecording" class="predict-button">结束录制</el-button>
				</div>
				<div class="button-section" style="margin-left: 20px">
					<el-button type="success" @click="submitDetection" :disabled="!state.recordedBlob || state.isRecording" class="predict-button">
						提交检测
					</el-button>
				</div>
				<div class="button-section" style="margin-left: 20px">
					<el-button @click="resetRecording" :disabled="state.isRecording" class="predict-button">重新录制</el-button>
				</div>
				<div class="demo-progress" v-if="state.isShow">
					<el-progress :text-inside="true" :stroke-width="20" :percentage=state.percentage style="width: 400px;">
						<span>{{ state.type_text }} {{ state.percentage }}%</span>
					</el-progress>
				</div>
			</div>
			<div class="cards" ref="cardsContainer">
				<div v-if="state.status === 'idle'" class="empty-guide">
					<p class="guide-title">请先录制课堂视频</p>
					<p>操作指引：选择模型/阈值/AI -> 开始录制 -> 结束录制 -> 提交检测。</p>
					<video ref="cameraVideoRef" v-show="state.showCameraPreview || state.isRecording" class="video" autoplay muted playsinline controls />
				</div>
				<div v-else-if="state.status === 'uploaded'" class="preview-panel">
					<p class="guide-title">录制完成，可先预览后提交检测</p>
					<video v-if="state.recordedVideoUrl" class="video" :src="state.recordedVideoUrl" controls />
				</div>
				<div v-else-if="state.status === 'processing'" class="processing-panel">
					<p class="guide-title">视频处理中，切换页面返回后仍会保持当前检测状态</p>
					<img v-if="state.video_path" class="video" :src="state.video_path">
				</div>
				<div v-else-if="state.status === 'success'" class="result-panel">
					<p class="guide-title">检测完成，以下为本次结果</p>
					<video v-if="state.latestResult.outVideo" class="video" controls preload="metadata">
						<source :src="state.latestResult.outVideo" type="video/mp4" />
					</video>
					<div class="result-desc">
						<div class="result-title">检测摘要与建议</div>
						<div class="result-text">{{ state.latestResult.kind || '暂无结果摘要' }}</div>
						<div v-if="state.latestResult.aiSuggestion" class="result-text" style="margin-top:8px;">
							AI建议：{{ state.latestResult.aiSuggestion }}
						</div>
					</div>
				</div>
				<div v-else class="empty-guide">
					<p class="guide-title">检测失败，请重新检测</p>
					<p>{{ state.errorMessage || '处理异常，请确认录制视频与网络后重试。' }}</p>
				</div>
			</div>
		</div>
	</div>
</template>


<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import request from '/@/utils/request';
import { useUserInfo } from '/@/stores/userInfo';
import { storeToRefs } from 'pinia';
import { SocketService } from '/@/utils/socket';
import { formatDate } from '/@/utils/formatTime';

const stores = useUserInfo();
const conf = ref(20);
const weight = ref('');
const { userInfos } = storeToRefs(stores);
const cameraVideoRef = ref<HTMLVideoElement | null>(null);
let mediaStream: MediaStream | null = null;
let mediaRecorder: MediaRecorder | null = null;
let recordingTimer: ReturnType<typeof setInterval> | null = null;
let recordedChunks: BlobPart[] = [];
const CAMERA_PREDICT_CACHE_KEY = 'camera_predict_page_state_v1';

const state = reactive({
	weight_items: [] as any,
	data: {} as any,
	video_path: '',
	type_text: "正在保存",
	percentage: 50,
	isShow: false,
	status: 'idle' as 'idle' | 'uploaded' | 'processing' | 'success' | 'failed',
	errorMessage: '',
	lastQueryParams: '',
	latestResult: {} as any,
	isRecording: false,
	recordingSeconds: 0,
	showCameraPreview: false,
	recordedBlob: null as Blob | null,
	recordedVideoUrl: '',
	alertMessage: '',
	form: {
		username: '',
		inputVideo: '',
		weight: '',
		conf: null as any,
		startTime: '',
		ai: ''
	},
});

const socketService = new SocketService();

socketService.on('message', (data) => {
	console.log('Received message:', data);
	ElMessage.success(typeof data === 'string' ? data : data?.data || '收到服务端消息');
});

const formatTooltip = (val: number) => {
	return val / 100
}

socketService.on('progress', (data) => {
	state.percentage = parseInt(data);
	if (parseInt(data) < 100) {
		state.isShow = true;
	} else {
		//两秒后隐藏进度条
		ElMessage.success("保存成功！");
		setTimeout(() => {
			state.isShow = false;
			state.percentage = 0;
		}, 2000);
	}
	console.log('Received message:', data);
	if (parseInt(data) >= 100 && state.status === 'processing') {
		fetchLatestResultWithRetry();
	}
	persistState();
});

socketService.on('alert', (payload: any) => {
	const ratio = payload?.ratio ? `（${payload.ratio}%）` : '';
	state.alertMessage = payload?.message || `检测到异常行为占比升高${ratio}`;
	ElMessage.warning(state.alertMessage);
});

socketService.on('video_result', (payload: any) => {
	if (!payload) return;
	state.latestResult = {
		...(state.latestResult || {}),
		outVideo: payload.outVideo || state.latestResult?.outVideo || '',
		kind: payload.kind || state.latestResult?.kind || '',
		aiSuggestion: payload.aiSuggestion || '',
	};
	if (state.status === 'processing' || state.status === 'success') {
		state.status = 'success';
		state.isShow = false;
		state.percentage = 100;
	}
	persistState();
});

socketService.on('camera_result', (payload: any) => {
	if (!payload) return;
	state.latestResult = {
		...(state.latestResult || {}),
		outVideo: payload.outVideo || state.latestResult?.outVideo || '',
		kind: payload.kind || state.latestResult?.kind || '',
		aiSuggestion: payload.aiSuggestion || '',
	};
	if (state.status === 'processing' || state.status === 'success') {
		state.status = 'success';
		state.isShow = false;
		state.percentage = 100;
	}
	persistState();
});

const persistState = () => {
	const payload = {
		video_path: state.video_path,
		type_text: state.type_text,
		percentage: state.percentage,
		isShow: state.isShow,
		status: state.status,
		errorMessage: state.errorMessage,
		lastQueryParams: state.lastQueryParams,
		latestResult: state.latestResult,
		recordedVideoUrl: state.recordedVideoUrl,
		alertMessage: state.alertMessage,
		form: state.form,
		weight: weight.value,
		conf: conf.value,
	};
	localStorage.setItem(CAMERA_PREDICT_CACHE_KEY, JSON.stringify(payload));
};

const restoreState = () => {
	try {
		const cached = localStorage.getItem(CAMERA_PREDICT_CACHE_KEY);
		if (!cached) return;
		const parsed = JSON.parse(cached);
		state.video_path = parsed.video_path || '';
		state.type_text = parsed.type_text || '正在保存';
		state.percentage = parsed.percentage || 0;
		state.isShow = !!parsed.isShow;
		state.status = parsed.status || 'idle';
		state.errorMessage = parsed.errorMessage || '';
		state.lastQueryParams = parsed.lastQueryParams || '';
		state.latestResult = parsed.latestResult || {};
		state.recordedVideoUrl = parsed.recordedVideoUrl || '';
		state.alertMessage = parsed.alertMessage || '';
		state.form = { ...state.form, ...(parsed.form || {}) };
		weight.value = parsed.weight || '';
		conf.value = parsed.conf || 20;
	} catch (error) {
		console.error('恢复摄像检测页面状态失败', error);
	}
};

const getData = () => {
	request.get('/api/flask/file_names').then((res) => {
		if (res.code == 0) {
			res.data = JSON.parse(res.data);
			console.log(res.data);
			state.weight_items = res.data.weight_items;
		} else {
			ElMessage.error(res.msg);
		}
	});
};

const startTimer = () => {
	stopTimer();
	state.recordingSeconds = 0;
	recordingTimer = setInterval(() => {
		state.recordingSeconds += 1;
	}, 1000);
};

const stopTimer = () => {
	if (recordingTimer) {
		clearInterval(recordingTimer);
		recordingTimer = null;
	}
};

const initCamera = async () => {
	if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
		throw new Error('当前浏览器不支持摄像头录制');
	}
	mediaStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
	if (!cameraVideoRef.value) return;
	cameraVideoRef.value.srcObject = mediaStream;
	state.showCameraPreview = true;
};

const startRecording = async () => {
	try {
		if (!weight.value) {
			ElMessage.warning('请先选择模型');
			return;
		}
		if (!mediaStream) {
			await initCamera();
		}
		if (!mediaStream) return;
		const mimeType = MediaRecorder.isTypeSupported('video/webm;codecs=vp8,opus')
			? 'video/webm;codecs=vp8,opus'
			: 'video/webm';
		recordedChunks = [];
		mediaRecorder = new MediaRecorder(mediaStream, { mimeType });
		mediaRecorder.ondataavailable = (event) => {
			if (event.data && event.data.size > 0) recordedChunks.push(event.data);
		};
		mediaRecorder.onstop = () => {
			state.recordedBlob = new Blob(recordedChunks, { type: mediaRecorder?.mimeType || 'video/webm' });
			if (state.recordedVideoUrl) URL.revokeObjectURL(state.recordedVideoUrl);
			state.recordedVideoUrl = URL.createObjectURL(state.recordedBlob);
			state.showCameraPreview = false;
			state.status = 'uploaded';
			persistState();
		};
		mediaRecorder.start();
		state.isRecording = true;
		state.status = 'idle';
		startTimer();
		state.errorMessage = '';
		state.latestResult = {};
		state.alertMessage = '';
		persistState();
		ElMessage.success('摄像头录制已开始');
	} catch (error: any) {
		ElMessage.error(error?.message || '无法启动摄像头录制，请检查权限');
	}
};

const stopRecording = () => {
	if (!mediaRecorder || mediaRecorder.state !== 'recording') return;
	mediaRecorder.stop();
	state.isRecording = false;
	stopTimer();
	persistState();
	ElMessage.success('录制结束，可预览并选择是否提交检测');
};

const uploadRecordedVideo = async () => {
	if (!state.recordedBlob) throw new Error('没有可上传的录制视频');
	const ext = state.recordedBlob.type.includes('mp4') ? 'mp4' : 'webm';
	const file = new File([state.recordedBlob], `camera_record_${Date.now()}.${ext}`, { type: state.recordedBlob.type || 'video/webm' });
	const formData = new FormData();
	formData.append('file', file);
	const response = await fetch('http://localhost:9999/files/upload', {
		method: 'POST',
		body: formData,
	});
	if (!response.ok) throw new Error('上传录制视频失败');
	const data = await response.json();
	if (!data || data.code !== '0') throw new Error(data?.msg || '上传录制视频失败');
	return data.data as string;
};

const submitDetection = async () => {
	try {
		if (!state.recordedBlob) {
			ElMessage.warning('请先录制视频');
			return;
		}
		state.form.weight = weight.value;
		state.form.conf = parseFloat(conf.value.toString()) / 100;
		state.form.username = userInfos.value.userName;
		state.form.startTime = formatDate(new Date(), 'YYYY-mm-dd HH:MM:SS');
		state.form.inputVideo = await uploadRecordedVideo();
		const queryParams = new URLSearchParams(state.form as any).toString();
		state.lastQueryParams = queryParams;
		state.video_path = `http://127.0.0.1:5000/predictVideo?${queryParams}`;
		state.status = 'processing';
		state.errorMessage = '';
		state.latestResult = {};
		state.isShow = true;
		state.percentage = 0;
		persistState();
		ElMessage.success('已提交检测，正在处理');
	} catch (error: any) {
		state.status = 'failed';
		state.errorMessage = error?.message || '提交检测失败';
		persistState();
		ElMessage.error(error?.message || '提交检测失败');
	}
};

const fetchLatestResult = (onEmpty?: () => void) => {
	request
		.get('/api/videoRecords', {
			params: {
				pageNum: 1,
				pageSize: 20,
				search: state.form.username,
				search1: state.form.startTime,
			},
		})
		.then((res) => {
			if (res.code !== 0) {
				state.status = 'failed';
				state.errorMessage = res.msg || '查询检测结果失败';
				ElMessage.error('检测失败，请重新检测');
				persistState();
				return;
			}
			const records = res.data?.records || [];
			const target = records.find((item: any) => item.startTime === state.form.startTime) || records[0];
			if (!target) {
				onEmpty?.();
			} else {
				state.latestResult = {
					...target,
					aiSuggestion: state.latestResult?.aiSuggestion || '',
				};
				state.status = 'success';
				state.isShow = false;
				state.percentage = 100;
				ElMessage.success('检测成功，结果已在当前页面展示');
			}
			persistState();
		})
		.catch(() => {
			state.status = 'failed';
			state.errorMessage = '查询检测结果失败，请重新检测';
			ElMessage.error('检测失败，请重新检测');
			persistState();
		});
};

const fetchLatestResultWithRetry = (retry = 5) => {
	fetchLatestResult(() => {
		if (retry > 0) {
			setTimeout(() => fetchLatestResultWithRetry(retry - 1), 1000);
			return;
		}
		state.status = 'failed';
		state.errorMessage = '未查询到本次检测记录，请重新检测';
		ElMessage.error('检测失败，请重新检测');
		persistState();
	});
};

const resetRecording = () => {
	if (state.recordedVideoUrl) URL.revokeObjectURL(state.recordedVideoUrl);
	state.recordedVideoUrl = '';
	state.recordedBlob = null;
	state.video_path = '';
	state.status = 'idle';
	state.errorMessage = '';
	state.lastQueryParams = '';
	state.latestResult = {};
	state.isShow = false;
	state.percentage = 0;
	state.alertMessage = '';
	state.showCameraPreview = true;
	localStorage.removeItem(CAMERA_PREDICT_CACHE_KEY);
	ElMessage.success('已重置，可重新录制');
};

const stopMediaTracks = () => {
	if (mediaStream) {
		mediaStream.getTracks().forEach((track) => track.stop());
		mediaStream = null;
	}
};

onMounted(() => {
	getData();
	restoreState();
	if (state.status === 'processing' && state.lastQueryParams && !state.video_path) {
		state.video_path = `http://127.0.0.1:5000/predictVideo?${state.lastQueryParams}`;
	}
});
</script>

<style scoped lang="scss">
.predict-button {
    background: #2196F3;
    border-color: #2196F3;
    &:hover {
        background: #1565C0;
        border-color: #1565C0;
    }
}
.system-predict-container {
	width: 100%;
	height: 100%;
	display: flex;
	flex-direction: column;

	.system-predict-padding {
		padding: 15px;

		.el-table {
			flex: 1;
		}
	}
}

.header {
	width: 100%;
	height: 5%;
	display: flex;
	justify-content: start;
	align-items: center;
	font-size: 20px;
}

.cards {
	width: 100%;
	height: 95%;
	border-radius: 5px;
	margin-top: 15px;
	padding: 0px;
	overflow: hidden;
	display: flex;
	justify-content: center;
	align-items: center;
	/* 防止视频溢出 */
}

.empty-guide,
.preview-panel,
.processing-panel,
.result-panel {
	width: 100%;
	height: 100%;
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	gap: 12px;
	color: #606266;
}

.guide-title {
	font-size: 16px;
	font-weight: 600;
	color: #303133;
}

.video {
	width: 100%;
	max-height: 100%;
	/* 限制视频最大高度不超过父元素高度 */
	height: auto;
	object-fit: contain;
}

.result-desc {
	width: 100%;
	padding: 12px;
	background: #f8fbff;
	border: 1px solid #d9ecff;
	border-radius: 8px;
}

.result-title {
	font-size: 14px;
	font-weight: 600;
	color: #1565c0;
	margin-bottom: 6px;
}

.result-text {
	font-size: 13px;
	line-height: 1.6;
	color: #333;
	white-space: pre-wrap;
	max-height: 180px;
	overflow-y: auto;
}

.button-section {
	display: flex;
	justify-content: center;
}

.predict-button {
	width: 100%;
	/* 按钮宽度填满 */
}

.demo-progress .el-progress--line {
	margin-left: 20px;
	width: 600px;
}
</style>