<template>
    <div id="front-desk">
        <img src="../assets/icon.png" alt="Icon" class="icon" />
        <div class="control-output-container">
            <div class="output-section" id="bill-output">{{ billContent }}</div>
            <div class="controls">
                <select v-model="selectedRoomForBill">
                    <option value="room1">Room1</option>
                    <option value="room2">Room2</option>
                    <option value="room3">Room3</option>
                    <option value="room4">Room4</option>
                    <option value="room5">Room5</option>
                </select>
                <button @click="generateBill">生成账单</button>
            </div>
        </div>
        <div class="control-output-container">
            <div class="output-section" id="details-output">{{ detailsContent }}</div>
            <div class="controls">
                <select v-model="selectedRoomForDetails">
                    <option value="room1">Room1</option>
                    <option value="room2">Room2</option>
                    <option value="room3">Room3</option>
                    <option value="room4">Room4</option>
                    <option value="room5">Room5</option>
                </select>
                <button @click="generateDetails">生成详单</button>
            </div>
        </div>
    </div>
</template>




<script>
export default {
    data() {
        return {
            selectedRoomForBill: '',
            selectedRoomForDetails: '',
            billContent: '',
            detailsContent: ''
        };
    },
    methods: {
        generateBill() {
            // 生成账单的逻辑
            this.billContent = "账单内容..."; // 这里你可以添加真实的逻辑
        },
        generateDetails() {
            // 生成详单的逻辑
            this.detailsContent = "详单内容..."; // 同样，添加真实的逻辑
        }
    }
}
</script>

<style scoped>
.icon {
    position: absolute;
    /* 绝对定位图标 */
    top: 20px;
    /* 距顶部的距离 */
    left: 20px;
    /* 距左侧的距离 */
    width: 70px;
    /* 您期望的大小 */
    height: auto;
    /* 保持纵横比 */
}

#front-desk {
    background-image: url('../assets/2023.10.30.jpg');
    background-size: auto;
    background-position: center;
    background-attachment: scroll;
    display: flex;
    flex-direction: column;
    align-items: center;
    /* 水平居中 */
    justify-content: center;
    /* 现在添加垂直居中 */
    padding: 20px;
    padding-top: 40px;
    /* 顶部增加内边距，为图标空间留出位置 */
    min-height: 95vh;
    min-width: 95vw;
    /* 添加最小高度为视口高度，确保有足够的垂直空间进行居中 */
    position: relative;
}

.control-output-container {
    display: flex;
    flex-direction: row;
    /* 改为水平布局 */
    justify-content: center;
    /* 子项之间保持间隔 */
    align-items: center;
    /* 在交叉轴上居中对齐 */
    width: 100%;
    margin-bottom: 20px;
    /* 容器间距 */
}

.controls {
    display: flex;
    align-items: center;
    /* 控件垂直居中 */
    /* 不再需要margin-left，因为选择框和按钮是并排的 */
}

select,
button {
    margin-right: 10px;
    /* 控件之间的间隔 */
}

select {
    height: 30px;
    /* 选择框高度 */
    padding: 0 10px;
    /* 选择框内部的左右内边距 */
    border: 1px solid #ccc;
    border-radius: 4px;
}

button {
    height: 30px;
    /* 按钮高度，与选择框相同 */
    padding: 0 10px;
    /* 按钮内边距 */
    border-radius: 4px;
    background-color: #007bff;
    color: white;
    font-size: 14px;
    /* 字体大小，根据高度调整 */
    border: none;
    cursor: pointer;
    line-height: 30px;
    /* 行高与按钮高度相同以垂直居中文本 */
    white-space: nowrap;
    /* 防止文本换行 */
    overflow: hidden;
    /* 隐藏溢出的文本 */
}

button:hover {
    background-color: rgb(252, 195, 97);
}

.button:active {
    /* 点击时的样式 */
    background-color: #ddd;
    color: black;
}

.output-section {
    background-color: rgba(255, 255, 255, 0.244);
    border: 1px solid #ccc;
    padding: 10px;
    width: 500px;
    /* 减去选择框和按钮的宽度 */
    height: 200px;
    /* 输出框高度 */
    overflow: auto;
    margin-right: 10px;
    margin-bottom: 10px;
    /* 输入框之间的间隔 */
    box-sizing: border-box;
    /* 包括内边距和边框在内的总宽度 */
    border: 2px solid #ccc;
    /* 边框样式 */
    border-radius: 4px;
    /* 边框圆角 */
    font-size: 20px;
    font-weight: bold;
    font-feature-settings: "tnum";
    /* 字体大小 */
}

@media (max-width: 768px) {

    input[type="text"],
    input[type="password"],
    select,
    button {
        width: 100%;
    }
}
</style>

