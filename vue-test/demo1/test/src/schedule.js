import request from "@/request";

export function power_on() {
  return request.get('/api/schedule/poweron', null, {
  })
}


export function show() {
  return request.get('/api/schedule/show', null, {
  })
}

export function request_on(p1) {
  return request.post('/api/schedule/request_on', null, {
    params: {
        room_id: p1,
    },
  })
}

export function request_off(p1) {
  return request.post('/api/schedule/request_off', null, {
    params: {
        room_id: p1,
    },
  })
}

export function request_temp(p1,p2) {
  return request.post('/api/schedule/request_temp', null, {
    params: {
        room_id: p1,
        target_temperature: p2,
    },
  })
}

export function request_speed(p1,p2) {
  return request.post('/api/schedule/request_speed', null, {
    params: {
        room_id: p1,
        fan_speed: p2,
    },
  })
}