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
				<el-upload v-model="state.form.inputVideo" ref="uploadFile" class="avatar-uploader"
					action="http://localhost:9999/files/upload" :show-file-list="false"
					:on-success="handleAvatarSuccessone">
					<div class="button-section" style="margin-left: 20px">
						<el-button type="info" class="predict-button">上传视频</el-button>
					</div>
				</el-upload>
				<div class="button-section" style="margin-left: 20px">
					<el-button type="primary" @click="upData" :disabled="state.status === 'processing'" class="predict-button">开始处理</el-button>
				</div>
				<div class="button-section" style="margin-left: 20px">
					<el-button @click="resetPageState" :disabled="state.status === 'processing'" class="predict-button">重置</el-button>
				</div>
				<div class="demo-progress" v-if="state.isShow">
					<el-progress :text-inside="true" :stroke-width="20" :percentage=state.percentage style="width: 400px;">
						<span>{{ state.type_text }} {{ state.percentage }}%</span>
					</el-progress>
				</div>
			</div>
			<div class="cards" ref="cardsContainer">
				<div v-if="state.status === 'idle'" class="empty-guide">
					<p class="guide-title">请先上传课堂视频</p>
					<p>操作指引：选择模型/阈值 -> 上传视频 -> 开始处理。</p>
				</div>

				<div v-else-if="state.status === 'uploaded'" class="preview-panel">
					<p class="guide-title">上传成功，可先预览视频后再提交检测</p>
					<video v-if="state.form.inputVideo" class="video" controls preload="metadata">
						<source :src="state.form.inputVideo" type="video/mp4" />
					</video>
				</div>

				<div v-else-if="state.status === 'processing'" class="processing-panel">
					<p class="guide-title">视频处理中，切换页面后返回将继续保持当前状态</p>
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
					<p>{{ state.errorMessage || '处理异常，请确认视频与网络后重试。' }}</p>
				</div>
			</div>
		</div>
	</div>
</template>


<script setup lang="ts">
import { reactive, ref, onMounted, onActivated, onDeactivated } from 'vue';
import { ElMessage } from 'element-plus';
import request from '/@/utils/request';
import { useUserInfo } from '/@/stores/userInfo';
import { storeToRefs } from 'pinia';
import type { UploadInstance, UploadProps } from 'element-plus';
import { SocketService } from '/@/utils/socket';
import { formatDate } from '/@/utils/formatTime';

const uploadFile = ref<UploadInstance>();
const VIDEO_PREDICT_CACHE_KEY = 'video_predict_page_state_v1';
const hasDeactivatedOnce = ref(false);
const stores = useUserInfo();
const conf = ref(20);
const weight = ref('');
const { userInfos } = storeToRefs(stores);

const handleAvatarSuccessone: UploadProps['onSuccess'] = (response, uploadFile) => {
	ElMessage.success('上传成功！');
	state.form.inputVideo = response.data;
	state.status = 'uploaded';
	state.errorMessage = '';
	persistState();
};
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
	form: {
		username: '',
		inputVideo: null as any,
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
		form: state.form,
		weight: weight.value,
		conf: conf.value,
	};
	localStorage.setItem(VIDEO_PREDICT_CACHE_KEY, JSON.stringify(payload));
};

const restoreState = () => {
	try {
		const cached = localStorage.getItem(VIDEO_PREDICT_CACHE_KEY);
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
		state.form = { ...state.form, ...(parsed.form || {}) };
		weight.value = parsed.weight || '';
		conf.value = parsed.conf || 20;
	} catch (error) {
		console.error('恢复视频检测页面状态失败', error);
	}
};

const resetPageState = (showMessage = true) => {
	state.video_path = '';
	state.isShow = false;
	state.percentage = 0;
	state.status = 'idle';
	state.errorMessage = '';
	state.lastQueryParams = '';
	state.latestResult = {};
	state.form.inputVideo = null;
	localStorage.removeItem(VIDEO_PREDICT_CACHE_KEY);
	if (showMessage) {
		ElMessage.success('页面状态已重置');
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


const upData = () => {
	if (!weight.value) {
		ElMessage.warning('请先选择模型');
		return;
	}
	if (!state.form.inputVideo) {
		ElMessage.warning('请先上传视频');
		return;
	}
	state.form.weight = weight.value;
	state.form.conf = parseFloat(conf.value.toString()) / 100;
	state.form.username = userInfos.value.userName;
	state.form.startTime = formatDate(new Date(), 'YYYY-mm-dd HH:MM:SS');
	console.log(state.form);
	const queryParams = new URLSearchParams(state.form).toString();
	state.lastQueryParams = queryParams;
	state.video_path = `http://127.0.0.1:5000/predictVideo?${queryParams}`;
	state.status = 'processing';
	state.errorMessage = '';
	state.latestResult = {};
	state.isShow = true;
	state.percentage = 0;
	persistState();
	ElMessage.success('已提交检测，正在处理');
};

onMounted(() => {
	getData();
	restoreState();
	if (state.status === 'processing' && state.lastQueryParams && !state.video_path) {
		state.video_path = `http://127.0.0.1:5000/predictVideo?${state.lastQueryParams}`;
	}
});

onDeactivated(() => {
	hasDeactivatedOnce.value = true;
});

onActivated(() => {
	// 按需求：检测成功后离开页面，再返回应恢复为待上传初始态
	if (hasDeactivatedOnce.value && state.status === 'success') {
		resetPageState(false);
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