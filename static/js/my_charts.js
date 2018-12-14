
var ctx1 = document.getElementById("placeholder");
var ctx2 = document.getElementById("butthole");
var ctx3 = document.getElementById("waddup");

var bar_chart = new Chart(ctx1, {
    type: 'bar',
    data: {
        labels: ["Red", "Blue", "Yellow", "Green", "Purple", "Orange"],
        datasets: [{
            label: '# of Votes',
            data: [12, 19, 3, 5, 2, 3],
            backgroundColor: [
                'rgba(255, 99, 132, 0.2)',
                'rgba(54, 162, 235, 0.2)',
                'rgba(255, 206, 86, 0.2)',
                'rgba(75, 192, 192, 0.2)',
                'rgba(153, 102, 255, 0.2)',
                'rgba(255, 159, 64, 0.2)'
            ],
            borderColor: [
                'rgba(255, 99, 132, 1)',
                'rgba(54, 162, 235, 1)',
                'rgba(255, 206, 86, 1)',
                'rgba(75, 192, 192, 1)',
                'rgba(153, 102, 255, 1)',
                'rgba(255, 159, 64, 1)'
            ],
            borderWidth: 1
        }]
    },
    options: {
        scales: {
			   gridLines: [{
					color: 'rgba(192, 192, 192, 1)'
				}],

            yAxes: [{
                ticks: {
                    beginAtZero:true
                }
            }]
        }
    }
});


var doughnut_chart = new Chart(ctx2, {
	type:"doughnut",
	data:{
		labels:["Red","Blue","Yellow"],
		datasets:[{
			label:"My First Dataset",
			data:[300,50,100],
			backgroundColor:["rgb(255,99,132)","rgb(54,162,235)","rgb(255,205,86)"]
		}]
	}
});

var polar_chart = new Chart(ctx3, {
	type:"polarArea",
	data:{
		// These labels appear in the legend and in the tooltips when hovering different arcs
		labels:["Red","Green","Yellow","Grey","Blue"],
		datasets:[{
			label:"My First Dataset",
			data:[11,16,7,3,14],
			backgroundColor:["rgb(255, 99, 132)","rgb(75, 192, 192)","rgb(255, 205, 86)","rgb(201, 203, 207)","rgb(54, 162, 235)"
			]
		}]
	}
});
