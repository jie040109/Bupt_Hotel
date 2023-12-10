<template>
  <div id="app">
    <div class="container">
      <!-- Logo 和 Icon -->
      <div class="header">
        <img src="../assets/icon.png" alt="Icon" class="icon" />
      </div>

      <!-- HomeView 的内容 -->
      <div class="content">
        <h1>BUPT-Hotel</h1>
        <!-- 其余的 HomeView 内容 -->

        <div>
          <label for="identity">选择身份:</label>
          <select v-model="identity" @change="onIdentityChange">
            <option value="customer">Costumer</option>
            <option value="front_desk">Front Desk</option>
            <option value="administrator">Administrator</option>
          </select>

          <div v-if="identity === 'customer'">
            <label for="room">选择房间:</label>
            <select v-model="room">
              <option value="room1">Room1</option>
              <option value="room2">Room2</option>
              <option value="room3">Room3</option>
              <option value="room4">Room4</option>
              <option value="room5">Room5</option>
            </select>
          </div>
        </div>

        <div>
          <label for="account">用户账号:</label>
          <input type="text" v-model="account">
        </div>

        <div>
          <label for="password">用户密码:</label>
          <input type="password" v-model="password">
        </div>

        <button @click="submit">登录</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      identity: 'customer',
      room: 'room1',
      account: '',
      password: ''
    };
  },
  methods: {
    onIdentityChange() {
      // 当身份更改时，可以在这里执行特定操作
    },
    submit() {
      // 根据选择的身份跳转到相应页面
      if (this.identity === 'customer') {
        this.$router.push(`/room/${this.room}`);
      } else if (this.identity === 'front_desk') {
        this.$router.push('/front-desk');
      } else if (this.identity === 'administrator') {
        this.$router.push('/control-room');
      }
      // 这里应该还有一段验证账号密码的逻辑
    }
  }
}
</script>

<style scoped>
/* 添加背景图 */

.container {
  background-image: url('../assets/2023.10.30.jpg');
  background-size: auto;
  background-position: center;
  background-attachment: scroll;
  min-height: 100vh;
  min-width: 95vw;
  /* 垂直堆叠子元素 */
  position: relative;
}

/* 样式调整为适应新布局 */
.header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 20px;
}

.icon {
  /* Icon 的样式 */
  width: 70px;
  /* 或者您期望的尺寸 */
}

.content {
  /* 适当调整内容区域的样式 */
  width: 50%;
  display: flex;
  flex-direction: column;
  /* 适当调整内容区域的样式 */
  max-width: 400px;

  margin: auto;
  padding: 20px;
  position: relative;

  background-color: rgba(255, 255, 255, 0.814);
  /* 可以提供一点透明度以显示背景 */
  gap: 40px;
  border-radius: 16px;
}

/* 设置输入框和下拉菜单的宽度和高度 */
/* 设置文本和密码输入框的共通样式 */
select {
  width: 80%;
  /* 或者您可以使用具体的像素值，例如：width: 300px; */
  height: 40px;
  /* 或根据您的设计要求调整 */
  padding: 10px;
  /* 文本内部的左右内边距 */
  margin-bottom: 10px;
  /* 控件之间的垂直间距 */
  box-sizing: border-box;
  /* 确保内边距和边框不会增加控件的宽度 */
  border: 1px solid #ccc;
  /* 控件边框样式 */
  border-radius: 4px;
  /* 控件边框圆角 */
}

input[type="text"],
input[type="password"] {
  width: 80%;
  /* 宽度充满容器 */
  height: 40px;
  /* 输入框的高度 */
  padding: 0px;
  /* 内边距，左右各10像素 */
  margin-bottom: 10px;
  /* 输入框之间的间隔 */
  box-sizing: border-box;
  /* 包括内边距和边框在内的总宽度 */
  border: 1px solid #ccc;
  /* 边框样式 */
  border-radius: 4px;
  /* 边框圆角 */
  font-size: 16px;
  /* 字体大小 */
}

/* 如果需要，也可以为按钮设置样式 */
button {
  width: 100%;
  /* 按钮宽度与输入框相同 */
  height: 40px;
  /* 按钮高度 */
  padding: 10px;
  /* 按钮内边距 */
  margin-top: 0px;
  align-self: center;
  /* 与上方元素的间隔 */
  border: none;
  /* 无边框 */
  border-radius: 4px;
  /* 边框圆角 */
  background-color: #007bff;
  /* 背景颜色 */
  color: white;
  /* 字体颜色 */
  font-size: 16px;
  /* 字体大小 */
  cursor: pointer;
  /* 鼠标悬停时的光标样式 */
}

/* 调整后的样式确保了账号和密码输入框在视觉上的一致性 */


/* 为了响应不同屏幕尺寸，可以使用媒体查询来调整宽度 */
@media (max-width: 768px) {

  input[type="text"],
  input[type="password"],
  select,
  button {
    width: 100%;
  }
}

/* 其他样式 */
</style>