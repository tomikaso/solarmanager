let slideIndex = 0;
let maxSlides = 90;
let file1 = 'history/electricpower';
let file2 = 'history/boiltemp';
let file3 = 'history/housetemp';
let file4 = 'history/solarsum';
showSlides(slideIndex);

function filename1() {
              let res = file1 + dateNumber(slideIndex) + ".png";
              return res;
              }
function filename2() {
              let res = file2 + dateNumber(slideIndex) + ".png";
              return res;
              }
function filename3() {
              let res = file3 + dateNumber(slideIndex) + ".png";
              return res;
              }
function filename4() {
              let res = file4 + dateNumber(slideIndex) + ".html";
              return res;
              }

function plusSlides(n) {
  if (n < 0){slideIndex++;}
	else {slideIndex = slideIndex -1;}
  if (slideIndex > maxSlides){slideIndex = 0;}
  if (slideIndex < 0){slideIndex = maxSlides;}
  showSlides(slideIndex);
}


function showSlides(n) {
        if (n == 0) {
                document.getElementById("power1").src = 'electricpower.png';
                document.getElementById("boil1").src = 'boiltemp.png';
                document.getElementById("house1").src = 'housetemp.png';
                document.getElementById("headline").style.height = "50px";
                document.getElementById("headline").innerHTML = '<h1>kunterbunt solarmanager</h1>';
                }
              else {
                document.getElementById("power1").src = filename1();
                document.getElementById("boil1").src = filename2();
                document.getElementById("house1").src = filename3();
                document.getElementById("headline").innerHTML = '<object id="status" class="obj" width="700" type="text/html" ></object>';
                document.getElementById("headline").style.height = "50px";
                document.getElementById("status").data = filename4();
              }

}
function dateNumber(m) {
			  let shortDate = new Date()
              shortDate.setDate(shortDate.getDate() - m);
              yesterday = shortDate.toISOString().slice(0,10);
              return yesterday.replaceAll("-", "");
}