$(document).ready(function(){
	var data = [
		"{{ page.comment }}",
		[
				{% for r in page.rank %}
				{ t:"{{ r.rank }}", w:"{{ r.keyword }}" },
				{% endfor %}
		]
	];
	$(".boxes.weekly .onethird p, #menu p").html(data[0]);
	for ( var i=0,c=data[1].length; i<c; i++ ) {
		var r = data[1][i];
		var rank = $("<div/>",{ class: "rank" });
		rank.append($("<span/>",{ class: "num" }).append(i+1));
		rank.append($("<span/>",{ class: r.t }));
		rank.append($("<span/>",{ class: "word" }).append(r.w));
		$(".boxes.weekly .twothird").append(rank);
	}
	$("#menu .switch").click(function(){
		$("#menu").toggleClass("open");
	});
	$(".box").each(function( i, el ){
		if ( !$(el).hasClass("on") && $(el).offset().top + 100 < $(window).scrollTop()+$(window).height() ) {
			$(el).addClass("on");
		}
		$(window).on("scroll", function(){
			if ( !$(el).hasClass("on") && $(el).offset().top + 100 < $(window).scrollTop()+$(window).height() ) {
				$(el).addClass("on");
			}
		});
	});
});
