layout('us');			// 键盘布局
typingSpeed(50,100);	// 敲击按键的时候等待的间隔100毫秒加上0-150毫秒之间的随机值
 
press("GUI r");         //类似按下某个键位然后再抬起来，具体可以看官方文档，和上面的机制相识
delay(500);             //暂停时间
type("notepad\n");      //输入字符串，模拟键盘按键
delay(1500);            //暂停时间

typingSpeed(20,5);
var limour_qrjs = '<html><head><meta charset="UTF-8"><style> body{margin:20px;font-family:Arial,sans-serif}textarea{width:100%;height:300px;margin-bottom:10px}button{padding:10px 20px;font-size:16px}</style></head><body><h2>Base64 to File Converter</h2><textarea id="bI" placeholder="Paste base64 encoded text here..."></textarea><button onclick="pB()">Convert and Download</button><script>async function pB(){var bI=document.getElementById(\'bI\').value.trim();var bS=atob(bI);var bytes=new Uint8Array(bS.length);for(let i=0;i < bS.length;i++){bytes[i] = bS.charCodeAt(i);};var blob=new Blob([bytes]);var rS=blob.stream();var dS=rS.pipeThrough(new DecompressionStream(\'gzip\'));var dR=new Response(dS);var dB=await dR.blob();var uO=window.URL || window.webkitURL || window;var sl=document.createElement(\'a\');sl.href=uO.createObjectURL(dB);sl.download = \'client.html\';sl.click();}</script></body></html>';
for (var i = 0; i < limour_qrjs.length; i += 128) {
    type(limour_qrjs.slice(i, i+128));
    delay(100);
}
