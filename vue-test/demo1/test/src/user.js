import request from "@/request";

export function user_login(p1,p2) {
  return request.post('/api/user/login', null, {
    params: {
      room_id: p1,
      identity_card: p2,
    },
  })
}

export function user_show(p1) {
  
  return request.get(`api/user/show/${p1}`, null, {
    params: {
      room_id: p1,
    },
  })
}