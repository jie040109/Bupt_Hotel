<!-- 

template: 定义组件的HTML模板   梁铮越
script: 定义组件的行为、通信连接 王俊杰
style: 定义组件的样式         梁铮越

 -->


 <!-- 

页面构建完成：12.14  梁铮越
初始通信连接 12.15   王俊杰
添加生成excel文件功能 12.16  王俊杰
删除页面框图,添加账单图片 12.16  梁铮越

  -->

<template>
    <div id="front-desk">
        <img src="../assets/icon.png" alt="Icon" class="icon" />
        <div class="combined-container">
            <img src="../assets/FD_static.png" alt="mid-pic" class="static-image-container" />
            <div class="control-output-container">
                <div class="controls">
                    <input type="number" v-model="roomNumberForBill" placeholder="Enter room number">
                    <button @click="generateBill">生成账单</button>
                </div>
                <div class="controls">
                    <input type="number" v-model="roomNumberForDetails" placeholder="Enter room number">
                    <button @click="generateDetails">生成详单</button>
                </div>
            </div>
        </div>
        <div class="checkout">
            <button @click="checkOut">退房</button>
        </div>
    </div>
</template>




<script>


import { admin_getrecords, admin_getbills, admin_delete } from "@/admin";
import * as XLSX from 'xlsx';
import { saveAs } from 'file-saver';


export default {
    data() {
        return {
            billContent: '',
            detailsContent: '',
            roomNumberForBill: '', // 新增的输入属性
            roomNumberForDetails: '', // 新增的输入属性
        };
    },
    methods: {
        async generateBill() {
            // 生成账单的逻辑
            if (this.roomNumberForBill) {
                const roomId = parseInt(this.roomNumberForBill, 10);
                const response = await admin_getbills(roomId);
                console.log(response.data);
                //this.billContent = [response.data]; 
                const wb = XLSX.utils.book_new();
                const ws = XLSX.utils.json_to_sheet(this.billContent);
                XLSX.utils.book_append_sheet(wb, ws, "Bills");
                const wbout = XLSX.write(wb, { bookType: "xlsx", type: "binary" });
                function s2ab(s) {
                    const buffer = new ArrayBuffer(s.length);
                    const view = new Uint8Array(buffer);
                    for (let i = 0; i < s.length; i++) {
                        view[i] = s.charCodeAt(i) & 0xFF;
                    }
                    return buffer;
                }
                const blob = new Blob([s2ab(wbout)], { type: "application/octet-stream" });
                saveAs(blob, "bills.xlsx");

            }
        },

        async generateDetails() {
            if (this.roomNumberForDetails) {
                try {
                    const roomId = parseInt(this.roomNumberForDetails, 10);
                    const response = await admin_getrecords(roomId);

                    // 确认response.data是期望的数组格式
                    console.log(response.data);

                    //this.detailsContent = response.data;

                    const wb = XLSX.utils.book_new();
                    const ws = XLSX.utils.json_to_sheet(this.detailsContent);
                    XLSX.utils.book_append_sheet(wb, ws, "Details");

                    const wbout = XLSX.write(wb, { bookType: "xlsx", type: "binary" });
                    function s2ab(s) {
                        const buffer = new ArrayBuffer(s.length);
                        const view = new Uint8Array(buffer);
                        for (let i = 0; i < s.length; i++) {
                            view[i] = s.charCodeAt(i) & 0xFF;
                        }
                        return buffer;
                    }
                    const blob = new Blob([s2ab(wbout)], { type: "application/octet-stream" });

                    // 使用file-saver的saveAs方法触发文件下载
                    saveAs(blob, "details.xlsx");
                } catch (error) {
                    console.error("生成详单时发生错误", error);
                }
            }

        },
        checkOut() {
            // 退房的逻辑

            if (this.roomNumberForBill) {
                const roomId = parseInt(this.roomNumberForBill, 10);
                admin_delete(roomId);
                alert("退房成功");
                
            }

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

.static-image-container {
    width: 500px;
    height: 500px;
  
    display: flex;
    justify-content: center;
    margin-bottom: 20px;
    object-fit: cover;
}

.combined-container {
    display: flex;
    justify-content: center;
    align-items: center;
}

.static-image-container {
    width: 500px;
    height: 500px;
    object-fit: cover;
    margin-right: 100px;
    /* 如果需要，可调整间隔 */
}

.static-image-container img {
    max-width: 100%;
    height: auto;
}

.control-output-container {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 100px;
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

input[type="number"] {
    width: 50px;
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

.checkout {
    display: flex;
    padding: 20px;
    position: relative;
    left: -8%;
}

@media (max-width: 768px) {

    input[type="text"],
    input[type="password"],
    select,
    c button {
        width: 100%;
    }
}
</style>