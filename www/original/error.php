<?php
$url = "http://asp.shime.tech/";
$site = "圧倒的成長プロジェクト";
$title = "４０４｜圧倒的成長プロジェクト";
$description = "";
$css = "top";
include("parts/header.php");
?>

<div class="blacket">
	<div class="left"></div>
	<h2>
		<span>今</span>
		<span>、</span>
		<span>流</span>
		<span>行</span>
		<span>り</span>
		<span>の</span>
		<span class="mobile"><br></span>
		<span>&nbsp;#&nbsp;</span>
		<span>ひ</span>
		<span>っ</span>
		<span>か</span>
		<span>け</span>
		<span>求</span>
		<span>人</span>
		<span>ワ</span>
		<span>ー</span>
		<span>ド</span>
	</h2>
	<div class="right"></div>
</div>
<?php include( "parts/weeklyranking.php" ); ?>
<div class="boxes category"></div>

<script>
var cats = [
	<?php for ( $i=0; $i<9; $i++ ): ?>
		[
			"エンジニア系",
			{ t:"same", w:"圧倒的成長" },
			{ t:"up", w:"海外インターン" },
			{ t:"down", w:"ゼロからつくる" },
			{ t:"same", w:"戦略的な" },
			{ t:"same", w:"第一人者" }
		],
	<?php endfor; ?>
];
for ( var i=0,c=cats.length; i<c; i++ ) {
	var b = cats[i];
	var box = $("<div/>",{ class: "box onethird" });
	box.append($("<h3/>").append(b.shift()));
	for ( var j=0,d=b.length; j<d; j++ ) {
		var r = b[j];
		var rank = $("<div/>",{ class: "rank" });
		rank.append($("<span/>",{ class: "num" }).append(j+1));
		rank.append($("<span/>",{ class: r.t }));
		rank.append($("<span/>",{ class: "word" }).append(r.w));
		box.append(rank);
	}
	$(".boxes.category").append(box);
}
$(window).on("load",function(){
	$(".blacket").addClass("on");
	setTimeout(function(){
		$("#menu, header, .blacket .left, .blacket .right, .box, footer").addClass("shown");
	}, 2600);
});
</script>
<?php include( "parts/footer.php" ); ?>
