dispatch = {

  employee: {
    endpoint: '/employee'
  },

  leave: {
    endpoint: '/leave_form'
  },

  settings: {
    endpoint: '/settings'
  }

}

actions = {

  post: function(resource, data, callback) {
    $.ajax({
      url: dispatch[resource].endpoint,
      method: 'POST',
      contentType: 'application/json',
      data: JSON.stringify(data),
      dataType: 'json',
      success: function(data) {
        callback('success', data)
      }
    })
  }

}