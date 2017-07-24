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


$('.datepicker').pickadate({
    selectMonths: true, // Creates a dropdown to control month
    selectYears: 15, // Creates a dropdown of 15 years to control year,
    today: 'Today',
    clear: 'Clear',
    close: 'Ok',
    closeOnSelect: false // Close upon selecting a date,
  });

$('select').material_select();

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

$('.newleave form').submit(function(e) {
  e.preventDefault()

  data = $(this).serializeArray()
  json_data = {}

  $.each(data, function() {
    json_data[this.name] = this.value
  })

  console.log(json_data)

  // @todo CSRF

  $.ajax({
    url: '/dashboard',
    method: 'POST',
    data: json_data,
    dataType: 'json',
    success: function() {
      console.log('Request Sent')
    }
  })

})