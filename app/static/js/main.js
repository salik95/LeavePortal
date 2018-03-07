lightbox = {
  show: function(lb) {
    $('body').css('overflow','hidden')
    lb.addClass('active')
    lb.fadeIn(400)
  },

  hide: function(lb) {
    $('body').css('overflow','inherit')
    lb.removeClass('active')
    lb.fadeOut(400)
  }
}

var getDate = function(d) {
  date = new Date(d)
  fixed_date = date.getFullYear() + '-' + (date.getMonth() + 1) + '-' + date.getDate()
  return fixed_date
}

$(document).ready(function() {
  var csrftoken = $('meta[name=csrf-token]').attr('content')

  $.ajaxSetup({
    beforeSend: function(xhr, settings) {
      if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type)) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken)
      }
    }
  })  
})



$('.datepicker').pickadate({
    selectMonths: true, // Creates a dropdown to control month
    selectYears: 15, // Creates a dropdown of 15 years to control year,
    today: 'Today',
    clear: 'Clear',
    close: 'Ok',
    closeOnSelect: false // Close upon selecting a date,
  })

$('select').material_select()

$('.tabs').tabs()

$('a.trigger').click(function(e) {
  e.preventDefault()
  id = $(this).attr('href')

  $lightbox = $('.lightbox'+id)

  lightbox.show($lightbox)

})

$('.lightbox').click(function(e) {
  if (e.target !== this)
    return;
  lightbox.hide($(this))
})

$('form[data-resource]').submit(function(e) {
  e.preventDefault()
  $self = $(this)
  $notice = $self.find('.notice')

  var resource = $self.attr('data-resource')
  var raw_data = $(this).serializeArray()
  var data = {}

  $.each(raw_data, function() {
    data[this.name] = this.value
  })

  // Prepare request data
  switch(resource) {
    case 'employee':
      data["date_of_joining"] = getDate(data["date_of_joining"])
      break
  }
  
  console.log(data)

  actions.post(resource, data, function(status, response) {
    if(status=='success') {
      console.log(response)
      $notice.removeClass('failure')
      $notice.addClass('success')
      $notice.text('Employee is successfully added and emailed.')
    }

    else {
      console.log('no bueno')
    }
  })
})