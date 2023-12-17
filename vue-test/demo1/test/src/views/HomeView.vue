<!-- 

template: 定义组件的HTML模板   梁铮越
script: 定义组件的行为、通信连接 王俊杰
style: 定义组件的样式         梁铮越

 -->

<!-- 

页面构建完成：12.14  梁铮越
初始通信连接 12.15   王俊杰
修改验证方式 12.15   梁铮越
添加密码双重验证 12.16  梁铮越

 -->

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

        <div class="form-row">
          <label for="identity">选择身份:</label>
          <select id="identity" v-model="identity" @change="onIdentityChange">
            <option value="customer">Costumer</option>
            <option value="front_desk">Front Desk</option>
            <option value="administrator">Administrator</option>
          </select>
        </div>

        <!-- 替换为手动输入房间号 -->
        <div class="form-row" v-if="identity === 'customer'">
          <label for="room">Room ID:</label>
          <input id="room" type="text" v-model="room">
        </div>

        <div class="form-row">
          <label for="password">Identity_card:</label>
          <input id="password" type="password" v-model="password">
        </div>

        <button @click="submit">登录</button>
      </div>
    </div>
  </div>
</template>


<script>
import { admin_login } from "@/admin";
import { user_login } from "@/user";
export default {
  data() {
    return {
      identity: 'customer',
      room: '',
      account: '',
      password: ''
    };
  },
  methods: {
    onIdentityChange() {
      // 当身份更改时，可以在这里执行特定操作
    },
    submit() {
      // 如果身份是管理员，尝试登录
      if (this.identity === 'administrator') {
        admin_login(this.password)
          .then(() => {
            // 登录成功，跳转到控制室页面
            this.$router.push('/control-room');
          })
          .catch(error => {
            // 登录失败，处理错误
            console.error(error);
          });
      } else if (this.identity === 'customer') {
        user_login(this.room, this.password)
          .then(() => {
            // 登录成功，跳转到房间页面
            this.$router.push(`/room/${this.room}`);
          })
          .catch(error => {
            // 登录失败，处理错误
            console.error(error);
          });
        // 如果身份是客户，跳转到房间页面
      } else if (this.identity === 'front_desk') {
        // 如果身份是前台，跳转到前台页面
        this.$router.push('/front-desk');
      }
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

.form-row {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  margin-bottom: 10px;
}

.form-row label {
  white-space: nowrap;
  /* Ensure the label text stays on one line */
  margin-right: 10px;
}

.form-width {
  width: 250px;
  /* Set the width you want for your inputs and selects */
  padding: 10px;
  box-sizing: border-box;
  border: 1px solid #ccc;
  border-radius: 4px;
  margin-right: 10px;
}


input[type="text"],

input[type="password"],
select {
  width: 70%;
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
  font-size: 14px;
  /* 字体大小 */
  margin-left: auto
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

.button:active {
  /* 点击时的样式 */
  background-color: #ddd;
  color: black;
}

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