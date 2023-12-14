import axios from 'axios';

const request = axios.create({
  changeOrigin: true,
  timeout: 5000,
  headers: {
    'Content-Type': 'application/json;charset=UTF-8'
  }
});

export default request;