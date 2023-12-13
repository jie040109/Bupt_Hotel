<template>
    <div :class="['room', customClass]">
        <div class="room-header">
            <h3>{{ roomNumber }}</h3>
        </div>
        <div class="room-body">
            <div class="room-state">状态:{{ state }}</div>
            <div class="room-info">
                <div class="room-temperature">温度:{{ temperature }}°C</div>
                <div class="room-wind-speed">风速: {{ windSpeed }}</div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'Room',
    props: {
        roomNumber: String,
        state: String,
        temperature: Number,
        windSpeed: String,
        customClass: String  // 接收额外的类名
    }
};
</script>

<style scoped>
.room {
    border: 1px solid #ddd;
    padding: 10px;
    border-radius: 5px;
    width: 250px;
    /* 设置房间的宽度 */
    height: 150px;
    background-color: rgba(255, 255, 255, 0.812);
}

.room-header {
    display: flex;
    justify-content: center;
    /* 居中对齐 */
    align-items: center;
    width: 100%;
    /* 设置宽度为100% */
}

.room-header h3 {
    text-align: center;
    /* 文本居中 */
    width: 100%;
    /* 设置宽度为100% */
}

.room-body {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 10px;
    align-items: center;
    font-size: 16px;

}

.room-info {
    display: flex;
    align-items: flex-start;

    flex-direction: column;
    margin-top: 10px;
    gap: 20px;

}

.room-state {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 10px;

}

/* 其他样式 */
</style>
