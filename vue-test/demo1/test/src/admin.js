import request from "@/request";

export function admin_login(p1,) {
  return request.post('/api/admin/login', null, {
    params: {
      password: p1,
    },
  })
}

export function admin_modify(p1,p2,p3,p4) {
  return request.post('/api/admin/modify', null, {
    params: {
        room_id: p1,
        target_temperature: p2,
        fan_speed: p3,
        status: p4, 
    },
  })
}

export function admin_create(p1,p2,p3) {
  return request.post('/api/admin/create', null, {
    params: {
        room_id: p1,
        identity_card: p2,
        initial_temperature: p3,

    },
  })
}

export function admin_getroom(p1) {
  return request.get('/api/admin/rooms/', null, {
    params: {
        room_id: p1,
    },
  })
}

export function admin_getroomlist() {
  return request.get('/api/admin/rooms', null, {
  })
}


export function admin_getrecords(p1) {
  return request.get(`api/admin/records/${p1}`,
  null,{
  
    params: {
        room_id: p1,
    },
  })
}

export function admin_getbills(p1) {
    return request.get(`api/admin/bills/${p1}`,{
    params: {
        room_id: p1,
    },
  })
}


export function admin_delete(p1) {
  return request.delete('api/admin/delete', {
    params: {
        room_id: p1,
    },
  })
}