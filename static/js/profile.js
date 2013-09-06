
function update_reviews() {
    $.getJSON(JsonUrl, function(json){       
        var rcontent = '<table class="reviews">'
        for (i in json){
            width = 19*json[i].rating;
            rcontent = rcontent+ '<tr><td rowspan="3"><img src="'+json[i].review_thumb+'"></td><td>From '+json[i].sender_name+' on '+json[i].created+':</td></tr>';             
            rcontent=rcontent+'<tr><td><span class="rating-starsOff" style="width:95px;"><span class="rating-starsOn" style="width:'+width+'px"></span></span>';
            rcontent=rcontent+'</td></tr><tr><td>'+json[i].content+'</td></tr>';
        }
        rcontent=rcontent+'<tr class="space"></tr></table>';
        $('#dumpreviews').html(rcontent);
    });
};

function user_rating(){
    $("#avgrating").find('.rating-starsOn').each(function() {
        w =$(this).text();
        $(this).width(w * $(this).height());
    })
}
