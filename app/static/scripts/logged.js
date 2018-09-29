$(document).ready(() =>{
  var quickviews = bulmaQuickview.attach();
  $(".navbar-burger").click(function() {
    $(".navbar-burger").toggleClass("is-active");
    $(".navbar-menu").toggleClass("is-active");
  });
  const player = new Plyr(document.querySelectorAll('.video-player'));
})

document.getElementById('searchbar').onkeypress = function(e){
  if (!e) e = window.event;
  var keyCode = e.keyCode || e.which;
  if (keyCode == '13'){
    window.location.href="/search?q=" + $('#searchbar').val()
    return false;
  }
}

$('.create-story').click(() => {
    $('.create-modal').addClass('is-active');
})

$('.create-modal-close').click(() => {
  $('.error-message').text("")
  $('.error-holder').css('display', 'none')
  $('.create-modal').removeClass('is-active');
})

$('.pmt-trigger').click(() => {
  $('.p-modal').addClass('is-active')
})

$('.p-modal-close').click(() => {
  $('.p-modal').removeClass('is-active')
})

$('.create-collection').click(() => {
  $('.collection-modal').addClass('is-active');
})

$('.collection-modal-close').click(() => {
  $('.error-message').text("")
  $('.error-holder').css('display', 'none')
  $('.collection-modal').removeClass('is-active');
  let $el = $('#collection-img');
  $el.wrap('<form>').closest('form').get(0).reset();
  $('#filename-holder').text("No picture selected")
  $el.unwrap();
})

$('.send-story').click((ev) => {
    $(ev.currentTarget).attr("disabled", "disabled").addClass('is-loading')
    let url = $('.story-link').val().length ? $('.story-link').val() : false
    if(url){
        $.ajax({
            type: "POST",
            url: '/v1/story',
            data: JSON.stringify({
                'tweet_url': url,
                'lmk': 'false'
            }),
            dataType: 'json',
            contentType: "application/json",
            success: () => {
                location.reload()
            }
        });
    } else {
        $('.send-story').removeAttr("disabled", "disabled").removeClass('is-loading')
        var errorMessage = "Obviously can't do this without a valid link :("
        $('.error-message').text(errorMessage)
        $('.error-holder').css('display', 'block')
    }
})

$('.send-collection').click((ev) => {
  $('.send-collection').attr("disabled", "disabled").addClass('is-loading')
  let title = $('#collection-title').val()
  let genre = $('#collection-genre').val()
  let desc = $('#collection-desc').val()
  if(!!title.length && !!genre.length && !!desc.length){
    if($('#collection-img')[0].files.length == 1){
      var payload=new FormData()
      payload.append('image',$("#collection-img")[0].files[0])
      payload.append('title',encodeURI(title))
      payload.append('genre',encodeURI(genre))
      payload.append('desc',encodeURI(desc))
      $.ajax({
        url:"/v1/collection",
        type:'POST',
        data: payload,
        cache:false,
        processData:false,
        contentType:false,
        error:function(){
            console.log("upload error")
        },
        success:function(data){
          location.reload()
        }
      })
    } else {
      $('.send-collection').removeAttr("disabled", "disabled").removeClass('is-loading')
      var errorMessage = "Make sure you've selected an image and try again"
      $('.c-error-message').text(errorMessage)
      $('.c-error-holder').css('display', 'block')
    }
  } else {
    $('.send-collection').removeAttr("disabled", "disabled").removeClass('is-loading')
    var errorMessage = "Make sure you've filled all fields and try again"
    $('.c-error-message').text(errorMessage)
    $('.c-error-holder').css('display', 'block')
  }
}) 

$(document).on('change', '#collection-img', (ev) => {
  let filename = $(ev.currentTarget)[0].files[0].name
  let fileType = $(ev.currentTarget)[0].files[0].type
  if(fileType.startsWith("image")){
    $('#filename-holder').text(filename)
  } else {
    let $el = $('#collection-img');
    $el.wrap('<form>').closest('form').get(0).reset();
    $('#filename-holder').text("No picture selected")
    $el.unwrap();
    var errorMessage = "Let's try that again ;)"
    $('.c-error-message').text(errorMessage)
    $('.c-error-holder').css('display', 'block')
  }
});

$(document).on('click', '.annotate-add', (ev) => {
  let that = $(ev.currentTarget)
  that.attr("disabled", "disabled").addClass('is-loading')
  let text = that.closest('.media-content').find('.annotate-tb').val()
  if(!!text.length){
    let payload = {
      "text": text,
      "tweet_id": that.data('tweetid'),
      "story_id": that.data('storyid')
    }
    $.ajax({
      url:"/v1/annotation",
      type:'POST',
      data: JSON.stringify(payload),
      dataType: 'json',
      contentType: "application/json",
      error:function(){
          that.removeAttr("disabled", "disabled").removeClass('is-loading is-dark').addClass('is-warning').text('Click to retry!')
      },
      success:function(data){
          let comment = $($('<div></div>').append($('#comment-template').html()))
          comment.find('.comment-img').attr('src', data['image'])
          comment.find('.comment-name').text(data['name'])
          comment.find('.comment-text').text(data['text'])
          comment.find('.comment-annotationid').attr('data-annotationid', data['annotation_id'])
          comment.find('.comment-annotationid').attr('data-tweetid', data['tweet_id'])
          comment.find('.comment-annotationid').attr('data-storyid', data['story_id'])
          comment.find('.comment-ts').text(data['timestamp'])
          that.closest('.finder-block').find('.comments-holder').find('.no-thread').remove()
          that.closest('.finder-block').find('.comments-holder').append(comment.html())
          that.removeAttr("disabled", "disabled").removeClass('is-loading')
          that.closest('.media-content').find('.annotate-tb').val("")
      }
    })
  } else {
    that.removeAttr("disabled", "disabled").removeClass('is-loading')
  }
})

$(document).on('click', '.annotate-del', (ev) => {
  if (confirm("Are you sure you want to delete this comment?")) {
    let that = $(ev.currentTarget)

    let payload = {
      "annotation_id": that.data('annotationid'),
      "tweet_id": that.data('tweetid'),
      "story_id": that.data('storyid')
    }
    $.ajax({
      url:"/v1/annotation",
      type:'DELETE',
      data: JSON.stringify(payload),
      dataType: 'json',
      contentType: "application/json",
      success:function(data){
          that.closest('.ch-comment').remove()
      }
    })
  }
})

$(document).on('click', '.add-to-collection', (ev) => {
  $('.atc-modal').addClass('is-active')
})

$(document).on('click', '.atc-modal-close', (ev) => {
  $('.atc-modal').removeClass('is-active');
})

$(document).on('click', '.trigger-atc', (ev) => {
  let that = $(ev.currentTarget)
  let collection_id = that.data('collectionid')
  let payload = {
    "action": "ADD",
    "story_id": that.data('storyid')
  }
  $.ajax({
    url:"/v1/collection/" + collection_id,
    type:'PUT',
    data: JSON.stringify(payload),
    dataType: 'json',
    contentType: "application/json",
    success:function(data){
        window.location.href="/collection/" + collection_id
    }
  })
})

$(document).on('click', '.rfc-trigger', (ev) => {
  ev.preventDefault()
  let that = $(ev.currentTarget)
  if (confirm("Are you sure you want to remove this story from this collection?")) {
    let collection_id = that.data('collectionid')
    let payload = {
      "action": "REMOVE",
      "story_id": that.data('storyid')
    }
    $.ajax({
      url:"/v1/collection/" + collection_id,
      type:'PUT',
      data: JSON.stringify(payload),
      dataType: 'json',
      contentType: "application/json",
      success:function(data){
          location.reload()
      }
    })
  }
})

$(document).on('click', '.feature-btn', (ev) => {
  let that = $(ev.currentTarget)
  let collection_id = that.data('collectionid')
  that.attr("disabled", "disabled").addClass('is-loading')
  if(confirm("Are you sure you want to feature this collection?")){
    $.ajax({
      url:"/v1/feature/" + collection_id,
      type:'GET',
      dataType: 'json',
      contentType: "application/json",
      success:function(data){
          window.location.href="/"
      }
    })
  } else {
    that.removeAttr("disabled", "disabled").removeClass('is-loading')
  }
})