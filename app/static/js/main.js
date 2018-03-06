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

$('#addemployee form').submit(function(e) {
  e.preventDefault()

  data = $(this).serializeArray()
  json_data = {}

  $.each(data, function() {
    json_data[this.name] = this.value
  })

  json_data["date_of_joining"] = getDate(json_data["date_of_joining"])

  console.log(json_data)

  // @todo CSRF

  $.ajax({
    url: '/employee',
    method: 'POST',
    contentType: 'application/json',
    data: JSON.stringify(json_data),
    dataType: 'json',
    success: function(data) {
      console.log(data)
    }
  })

})