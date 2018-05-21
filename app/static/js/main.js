$(document).ready(function() {

  if(logged_in) {
    init()
    accountDropdown()
    searchEmployee()

    handleAsyncForm()
    handleEncashment()
    holidaysHandler()
  }

  $('form').on('submit', function(e) {

    $form = $(this)
    $form.addClass('loading')

    $notice = $form.find('.notice')
    $notice.removeClass('error')
    $notice.removeClass('success')
    $form.find('[type="submit"]').addClass('disabled')
    
  })

})


var getDate = function(d) {
  date = new Date(d)
  fixed_date = date.getFullYear() + '-' + (date.getMonth() + 1) + '-' + date.getDate()
  return fixed_date
}

var updateQueryParam = function(param, value) {
  var url = window.location.origin + window.location.pathname
  var query_string = location.search.substring(1)
  var query_obj = {}
  if(query_string !== '') {
    query_obj = JSON.parse('{"' + decodeURI(query_string).replace(/"/g, '\\"').replace(/&/g, '","').replace(/=/g,'":"') + '"}')
  }

  query_obj[param] = value
  query_string = '?' + $.param(query_obj)

  window.location.href = url + query_string
}

/** Init
*** Initialize the application components
**/

function init() {
  var csrftoken = $('meta[name=csrf-token]').attr('content')

  $.ajaxSetup({
    beforeSend: function(xhr, settings) {
      if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type)) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken)
      }
    }
  })

  months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

  $('.modal').modal();
  // $('#modal1').modal('open')
  $('select').material_select()
  $('.menu').tabs()

  $('.datepicker').pickadate({
    selectMonths: true,
    selectYears: 15,
    today: 'Today',
    clear: 'Clear',
    close: 'Ok',
    closeOnSelect: false,
    format: 'mmm dd, yyyy',
    formatSubmit: 'yyyy-mm-dd'
  })

  var yesterday = new Date((new Date()).valueOf()-1000*60*60*24)

  var $from_date_field = $('input[name="from_date"]')

  from_date_picker = $from_date_field.pickadate('picker')
  to_date_picker = $('input[name="to_date"]').pickadate('picker')
  to_date_picker.set('disable', true)

  var leaves_remaining = $("[data-leaves_remaining]").data('leaves_remaining')

  from_date_picker.on({
    'set': function(prop) {
      if(prop.select !== "undefined") {

        var date = from_date_picker.get('select')
        if(date) {
          console.log(date.pick)
          date = new Date(date.pick)
        }
        else
          return
        to_date_picker.set('disable', false)
        to_date_picker.set('min', date)
        to_date_picker.set('max', new Date(date.valueOf()+(1000*60*60*24*(leaves_remaining-1))) )
      }
    }
  })


  from_date_picker.set('disable', [{
    from: [0,0,0], to: yesterday
  }])

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

      var $form = lb.find('form[data-resource]')

      if($form) {
        $notice = $form.find('.notice')
        $notice.removeClass('success')
        $notice.removeClass('error')
      }
    }
  }

  $('.lightbox').click(function(e) {
    if (e.target !== this) return;
    lightbox.hide($(this))
  })

  $('a.trigger').click(function(e) {
    e.preventDefault()
    id = $(this).attr('href')
    $lightbox = $('.lightbox'+id)
    lightbox.show($lightbox)
  })


  $('[data-query]').click(function(){
    pair = $(this).attr('data-query').split('=')
    updateQueryParam(pair[0], pair[1])
  })

}


/** Generic Handler
*** Use form method and resource spec to send async request and render response
**/

function handleAsyncForm() {
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

    actions.send(resource, method, data, function(status, response) {

      $self.removeClass('loading')
      $self.find('[type="submit"]').removeClass('disabled')

      if(status=='success') {

        console.log(response)
        $notice.removeClass('error')
        $notice.addClass('success')
        if(resource == 'employee')
          $notice.text('Employee is successfully added and notified via email')

        else if (resource == 'leave' && method == "POST")
          $notice.text('Application is sent successfully and pending for approval.')

        // @todo: add update data.approval on view 

        else if (resource == 'leave' && method == "PUT") {
          $notice.text('Application is successfully responded to')
          $self.addClass('disabled')
          $self.find('input, textarea, button').attr('disabled', 'disabled').addClass('disabled')
          $self.closest('.collection-item').addClass('responded')
          $self.closest('.collection-item').removeClass('pending')
          $self.closest('.collection-item').addClass((data.approval.toLowerCase()))
        }

        else if (resource == 'encashment' && method == "PUT") {
          $notice.text('Request is successfully completed')
          $self.addClass('disabled')
          $self.find('input, textarea, button').attr('disabled', 'disabled').addClass('disabled')
          $self.closest('.collection-item').addClass('responded')
          $self.closest('.collection-item').removeClass('pending')
          $self.closest('.collection-item').addClass((data.approval.toLowerCase()))
          if(response.redirect_url !== undefined)
            window.open(response.redirect_url, '_blank')
        }

        else {
          console.log('no bueno')
        }

        $self[0].reset()

      }

      else {
        $notice.removeClass('success')
        $notice.addClass('error')
        $notice.text('Something went wrong. Please make sure there are no errors in the submission and retry')
      }


    })

  })
}


/** Encashment Form Handler
*** Validate encashment request amount, show realtime calculations
**/

function handleEncashment() {

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
}


/** Employee Search Componenet
*** Enter employee name keywords, query search api and list filtered employees
**/

function searchEmployee() {
  $list = $('#names')
  var searching = false

  $("input[list=names]").on("input",function(e) {

    $input = $(this)
    $label = $input.siblings('label')
    var selected_id = null
    var keyword = $input.val()
    
    if(keyword.length < 3)
      return

    if(searching == true)
      return

    searching = true

    $label.addClass('loading')
    getEmployees(keyword, function(list) {
      $list.empty()

      list.forEach(function(item) {
        $option = $('<option value="'+item.name+'" data-id="'+item.id+'">'+item.designation+'</option>')
        $list.append($option)
      })

      searching = false
      $label.removeClass('loading')
    })

    $('datalist#names > option').each(function(item) {
      if( $(this).val() === keyword ) {
        selected_id = $(this).attr('data-id')
      }
    })

    if(selected_id) {

      console.log(selected_id)

      if($input.attr('data-proxy')) {
        $('input[name='+$input.attr('data-proxy')+']').val(selected_id)
      }

      // For adding to query param
      else {
        updateQueryParam('id', selected_id)
      }
    }
  })
}


/** Holidays Form handler
*** Transform field 
**/

function holidaysHandler() {
  var $edit = $('#gazetted_edit_btn');
  $('#form-holidays input').prop("disabled",true)

  $edit.click(function(){
    var $child = $edit.closest(".row").find("input");
    $child.each(function(){
      $(this).prop('disabled',false);
    })
    
  })
}


/** Account Dropdown Component
*** Drop personal account menu on hover
**/

function accountDropdown() {
  $('.account > i').on('mouseover', function(event) {
    console.log(event)
    $('.account').addClass('active')
  })

  $('.account').on('mouseleave', function(event) {
    console.log(event)
    if($('.account').hasClass('active'))
      $('.account').removeClass('active')
  })
}