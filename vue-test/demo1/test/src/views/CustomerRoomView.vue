<template>
    <div class="container">
        <!-- 上方横栏 -->
        <div class="header">
            <!-- <div class="iconpic">
        <img src="../assets/icon.png" alt="Icon" class="icon" />
      </div> -->
            <div class="room-container">
                    <div class="room-title">Room</div>
            </div>
            <div class="title-container">
                <div class="title">{{ id }}</div>
            </div>
            <button @click="toggleButton" class="toggle-button circle" :class="{ 'active-button': !isLocked }">{{ buttonText
            }}</button>
        </div>

        <!-- 下方正文 -->
        <div class="content">
            <!-- 左侧留白 -->
            <div class="left-margin"></div>

            <!-- 主体部分 -->
            <div class="main-content">
                <!-- 第一块部分 -->
                <div class="section section-state">
                    <div class="section-title">状态</div>
                    <div class="section-content">
                        <div class="left-content" :class="{ 'locked': isLocked }">风速：{{ windSpeed }}</div>
                        <div class="right-content" :class="{ 'locked': isLocked }">温度：{{ current_temperature }}</div>
                    </div>
                </div>

                <!-- 第二块部分 -->
                <div class="section section-setting">
                    <div class="section-title">设置</div>
                    <div class="section-content">
                        <div class="top-content">
                            <span>风速：</span>
                            <button @click="setWindSpeed('high')" class="circle"
                                :class="{ 'active-button': !isLocked }">高</button>
                            <button @click="setWindSpeed('medium')" class="circle"
                                :class="{ 'active-button': !isLocked }">中</button>
                            <button @click="setWindSpeed('low')" class="circle"
                                :class="{ 'active-button': !isLocked }">低</button>
                        </div>
                        <div class="bottom-content">
                            设定温度：
                            <input v-model="temperature" type="number" class="temperature-input" />
                            <button @click="updateTemperature(temperature)" class="circle" :disabled="isLocked"
                                :class="{ 'active-button': !isLocked }">确定</button>
                        </div>
                    </div>
                </div>

                <!-- 第三块部分 -->
                <div class="section section-query">
                    <div class="section-title">查询</div>
                    <div class="section-content">
                        <div class="query-content">当前消费金额：{{ consumption }}</div>
                    </div>
                </div>
            </div>

            <!-- 右侧留白 -->
            <div class="right-margin"></div>
        </div>
    </div>
</template>


<script>
import { request_on ,request_off,request_temp,request_speed} from '@/schedule';
import { user_show } from '@/user';
export default {
    props: ['id'],
    data() {
        return {
            buttonText: '关',
            windSpeed: 'xx',
            //mode: 'xx',
            temperature: 0,
            current_temperature: 0,
            consumption: 'xx',
            isLocked: true,
            timerId: null
        };
    },
    methods: {
        toggleButton() {
            if (this.buttonText === '关') {
                this.isLocked = false;
                // 当切换为“开”时的额外逻辑

                const roomId = parseInt(this.id.slice(-1), 10);
                request_on(roomId);
            } else {
                this.isLocked = true;
                // 当切换为“关”时的额外逻辑
                this.resetState();
                const roomId = parseInt(this.id.slice(-1), 10);
                request_off(roomId);
            }
            this.buttonText = this.buttonText === '开' ? '关' : '开';
        },
        setWindSpeed(speed) {
            if (!this.isLocked) {
                this.windSpeed = speed;
                const roomId = parseInt(this.id.slice(-1), 10);
                request_speed(roomId, speed);
            }
        },
        updateTemperature(temperature) {
            if (!this.isLocked) {
                this.temperature = parseInt(temperature);
                const roomId = parseInt(this.id.slice(-1), 10);
                request_temp(roomId, temperature);

            }
        },
        resetState() {
            // 当切换为“关”时的重置状态逻辑
            this.windSpeed = 'xx';
            //this.mode = 'xx';
            this.temperature = 0;
            this.consumption = 'xx';
        },
        async updateState() {
            
            const roomId = parseInt(this.id.slice(-1), 10);
            const response =  await user_show(roomId);
            console.log(response);
            this.current_temperature = response.data.current_temperature.toFixed(1);
            //this.temperature = response.data[0];
            this.windSpeed = response.data.fan_speed;
            //this.mode = response.mode;
            this.consumption = response.data.total_cost.toFixed(2);
            
        }
    },
    created() {
        if (!this.timerId) {
                    this.timerId = setInterval(() => {
                        this.updateState();
                    }, 5000);
                }
    },
    beforeDestroy() {
        if (this.timerId){
            clearInterval(this.timerId);
        }
        
    }
};
</script>



<style scoped>
.toggle-button:hover {
    background-color: rgb(252, 195, 97);
    /* 悬停时的背景颜色 */
    color: #fff;
    /* 悬停时的文字颜色 */
}

.top-content button:hover,
.bottom-content button:hover {
    background-color: rgb(252, 195, 97);
    /* 悬停时的背景颜色 */
    color: #fff;
    /* 悬停时的文字颜色 */
}

.container {
    background-image: url('../assets/2023.10.30.jpg');
    background-size: auto;
    background-position: center;
    background-attachment: scroll;
    min-height: 100vh;
    min-width: 95vw;
    text-align: center;
}

.circle {
    border: 2px solid #ccc;
    /* 边框大小和颜色 */
    border-radius: 5px;
    /* 边框圆角 */
}

.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px;
    margin-left: 47px;
    width: auto;
}

.locked {
    opacity: 0.5;
    /* 设置锁住状态的元素半透明 */
    pointer-events: none;
    /* 禁用点击事件 */
}

/* .iconpic {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 20px;
}

.icon {
  width: 70px;
} */

.room-container {
    flex: 0.9;
    /* 填充剩余空间 */
    text-align: right;
}

.room-title {
    font-size: 30px;
    font-weight: bold;
    margin-left: 40px;  /* 没用 */
}

.title-container {
    flex: 0.9;
    /* 填充剩余空间 */
    text-align: left;
}

.title {
    font-size: 30px;
    font-weight: bold;
    margin-left: 40px;
}

.toggle-button {
    font-size: 20px;
    /* 调整按钮字体大小 */
    margin-left: 10px;
    /* 调整按钮与文字的间距 */
}

.content {
    display: flex;
    justify-content: space-between;
    padding: 20px;
}

.left-margin,
.right-margin {
    flex: 1;
}

.main-content {
    display: flex;
    flex-direction: column;
    /* 垂直方向排列 */
    width: 400px;
    /* 容器宽度 */
    margin: 0 auto;
    /* 居中显示 */
    margin-top: 40px;
}

.section {
    border: 2px solid #ccc;
    border-radius: 8px;
    padding: 10px;
    margin-bottom: 10px;
    /* 添加下边距，使部分之间有间隔 */
    background-color: rgba(255, 255, 255, 0.814);
}

.section-setting {
    /* 设置 flex 布局 */
    display: flex;
    flex-direction: column;
    justify-content: center;
    /* 内容垂直方向居中 */
    align-items: center;
    /* 内容水平方向居中 */
}

.top-content {
    margin-bottom: 10px;
    /* 添加下边距，使内容与下方内容有间隔 */
}

.button {
    padding:  20px;
    font-size: 16px;
}

.content {
    display: flex;
    justify-content: space-between;
    padding: 20px;
}

.temperature-input {
    width: 80px;
}

.left-margin,
.right-margin {
    flex: 1;
}

.middle-section {
    flex: 4;
    display: flex;
    justify-content: space-between;
}

.section {
    border: 2px solid #ccc;
    /* 边框大小和颜色 */
    border-radius: 8px;
    /* 边框圆角 */
    padding: 10px;
    margin-bottom: 10px;
}

.section-title {
    font-size: 18px;
    font-weight: bold;
}

.section-content {
    display: flex;
    flex-direction: column;
}

.left-content,
.right-content,
.query-content {
    margin: 10px 0;
}

.top-content,
.bottom-content {
    display: flex;
    flex-wrap: wrap;
    margin: 10px 0;
}

.input {
    margin-right: 10px;
}</style>
