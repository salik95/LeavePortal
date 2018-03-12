dispatch = {

  employee: {
    endpoint: '/employee'
  },

  leave: {
    endpoint: '/leave_form',
    PUT: {
      endpoint: '/respond_request'
    }
  },

  settings: {
    endpoint: '/settings'
  }

}

// @TODO refactor

actions = {

  send: function(resource, method, data, callback) {

    if(method == 'POST')
      dispatch[resource].endpoint
    else
      dispatch[resource].method.endpoint

    $.ajax({
      url: dispatch[resource].endpoint,
      method: method,
      contentType: 'application/json',
      data: JSON.stringify(data),
      dataType: 'json',
      success: function(data) {
        callback('success', data)
      }
    })
  }

}

function getEmployees(keyword, callback) {
  obj = {};
  list = [
    {id: 1, name: 'Kebab'},
    {id: 3, name: 'Keema'}
  ]

  callback(list)
}