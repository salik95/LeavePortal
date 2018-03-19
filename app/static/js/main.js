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

  $('.modal').modal();
  // $('#modal1').modal('open')

  $('.account > i').on('mouseover', function(event) {
    console.log(event)
    $('.account').addClass('active')
  })

  $('.account').on('mouseleave', function(event) {
    console.log(event)
    if($('.account').hasClass('active'))
      $('.account').removeClass('active')
  })

  // @TODO: Refactor; update names scopes etc

  $list = $('#names')
  
  $("input[list=names]").on("keypress",function(e) {

    var keyword = $(this).attr('value');
    getEmployees(keyword, function(list) {
      $list.empty()
      console.log(list)
      list.forEach(function(item) {
       $list.append('<option value="'+item.first_name+'">'+item.id+'</option>')
     })
    }) 
  });
  
  $encash_form = $('#encashment form')
  $encash_input = $('#encashment form input[name="amount"]')
  $encash_button = $encash_form.find('button')

  var leaves_available = parseFloat($('[data-id="leaves_available"]').attr('data-val')) 
  var salary = parseFloat($('[data-id="salary"]').attr('data-val'))
  var amount_available = leaves_available*salary

  $encash_input.on('input', function() {
    console.log('Amount Updates')

    if($(this).val() == '') {
      $encash_button.addClass('disabled')
      $encash_form.attr('data-state', '')
      return
    }

    var amount = parseInt($(this).val())
    var amount_remaining = parseFloat((amount_available - amount).toFixed(2))
    var leaves_remaining = parseFloat((amount_remaining / salary).toFixed(2))

    console.log(amount_remaining)

    $('[data-id="amount_remaining"]').text(amount_remaining < 0 ? 0 : amount_remaining)
    $('[data-id="leaves_remaining"]').text(leaves_remaining < 0 ? 0 : leaves_remaining)

    if(amount_remaining < 0) {
      $encash_form.attr('data-state', 'errored')
      $encash_button.addClass('disabled')
    }

    else {
      $encash_button.removeClass('disabled')
      $encash_form.attr('data-state', 'updated')
    }
    
  })

  $encash_input.on('keydown', function() {
    console.log('Amount Key Pressed!')
  })


})

$('.datepicker').pickadate({
    selectMonths: true, // Creates a dropdown to control month
    selectYears: 15, // Creates a dropdown of 15 years to control year,
    today: 'Today',
    clear: 'Clear',
    close: 'Ok',
    closeOnSelect: false, // Close upon selecting a date,
    format: 'yyyy-mm-dd'
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
  var method = $self.attr('method') || 'POST'

  var raw_data = $(this).serializeArray()
  var data = {}

  $.each(raw_data, function() {
    data[this.name] = this.value
  })

  // Prepare request data
  switch(resource) {
    case 'employee':
    break
    case 'leave':
    break
  }
  
  console.log(data)

  actions.send(resource, method, data, function(status, response) {

    if(status=='success') {
      console.log(response)
      $notice.removeClass('failure')
      $notice.addClass('success')
      if(resource == 'employee')
        $notice.text('Employee is successfully added and notified via email')
      else if (resource == 'leave')
        $notice.text('Application is sent successfully and pending for approval.')

      else if (resource == 'leave' && method == "PUT") {

      }
      else {
        console.log('no bueno')
      }
    }
  })

})