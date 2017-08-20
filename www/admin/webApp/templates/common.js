
var cats = [
		{% for ranks in ranking %}
		[
				"{{ ranks.name }}",
				{% for r in ranks.rank %}
				{ t:"{{ r.rank }}", w:"{{ r.keyword }}", n:"{{ r.no }}" },
				{% endfor %}
		],
		{% endfor %}
];

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
		for ( var i=0,c=cats.length; i<c; i++ ) {
				var b;
				if(i == 0) {
						/* 殿堂入り */
						var l = [];
						for(var k = 0; k < 5; k++){
								for (;;) {
										var n = Math.floor( Math.random () * (cats[i].length - 1)) + 1;
										if(l.indexOf(n) == -1) {
												l.push(n);
												break;
										}
								}
						}
						var b = [cats[i][0], cats[i][l[0]], cats[i][l[1]], cats[i][l[2]], cats[i][l[3]], cats[i][l[4]]];
				} else {
						var b = cats[i];
				}
				var box = $("<div/>",{ class: "box onethird" });
				box.append($("<h3/>").append(b.shift()));
				for ( var j=0,d=b.length; j<d; j++ ) {
						var r = b[j];
						var rank = $("<div/>",{ class: "rank" });
						if(i == 0){
								rank.append($("<span/>",{ class: "num" }));
						} else {
								rank.append($("<span/>",{ class: "num" }).append(r.n));
						}
						rank.append($("<span/>",{ class: r.t }));														 
						rank.append($("<span/>",{ class: "word" }).append(r.w));
						box.append(rank);
				}
				$(".boxes.category").append(box);
		}		
});

$(window).on("load",function(){
	$(".blacket").addClass("on");
	setTimeout(function(){
		$("#menu, header, .blacket .left, .blacket .right, .box, footer").addClass("shown");
	}, 2600);
});

(function (app) {
		var loading_class = 'loading';
		var html = document.documentElement;
		loading_class = ' ' + loading_class + ' ';
		
		//未サポート
		if (!app || app.UNCACHED === app.status) {
				init();
				return;
		}
		
		//初期読み込み
		if (!localStorage.appcaching) {
				localStorage.appcaching = 1;
				init();
				return;
		}
		
		//キャッシュが古くなっている
		if (app.status === app.UPDATEREADY) {
				location.reload();
				return;
		}
		//更新不要
		if (app.status === app.IDLE || app.status === app.OBSOLETE) {
				init();
				return;
		}
		
		//ローディング開始
		html.className += loading_class;
		
		//更新不要
		app.addEventListener('cached', start);
		//更新なし
		app.addEventListener('noupdate', start);
		//更新不可
		app.addEventListener('obsolete', start);
		//キャッシュが古くなっている
		app.addEventListener('updateready', function () {
				location.reload();
		});
		//更新不可
		app.addEventListener('error', start);
		//timeout
		var timeout = setTimeout(start, 3000);
		
		function start () {
				if (start.fire) {
						return;
				}
				clearTimeout(timeout);
				start.fire = 1;
				html.className = html.className.replace(loading_class, '');
				init();
		}
		function init () {
		}
})(window.applicationCache);


