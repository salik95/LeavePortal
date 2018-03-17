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

    var endpoint = ''

    if(method == 'POST')
      endpoint = dispatch[resource].endpoint
    else {
      console.log(dispatch[resource])
      endpoint = dispatch[resource][method]['endpoint']
    }

    $.ajax({
      url: endpoint,
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
  // obj = {};
  
  $.ajax({
    url : '/employee/search',
    contentType: 'application/json',
    data: JSON.stringify({
      keyword: keyword,
      thin:''
    }),
    dataType: 'json',
    success: function(data) {
      callback(data)
    }
  })
}