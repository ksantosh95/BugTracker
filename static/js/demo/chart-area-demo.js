// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';

function number_format(number, decimals, dec_point, thousands_sep) {
  // *     example: number_format(1234.56, 2, ',', ' ');
  // *     return: '1 234,56'
  number = (number + '').replace(',', '').replace(' ', '');
  var n = !isFinite(+number) ? 0 : +number,
    prec = !isFinite(+decimals) ? 0 : Math.abs(decimals),
    sep = (typeof thousands_sep === 'undefined') ? ',' : thousands_sep,
    dec = (typeof dec_point === 'undefined') ? '.' : dec_point,
    s = '',
    toFixedFix = function(n, prec) {
      var k = Math.pow(10, prec);
      return '' + Math.round(n * k) / k;
    };
  // Fix for IE parseFloat(0.55).toFixed(0) = 0;
  s = (prec ? toFixedFix(n, prec) : '' + Math.round(n)).split('.');
  if (s[0].length > 3) {
    s[0] = s[0].replace(/\B(?=(?:\d{3})+(?!\d))/g, sep);
  }
  if ((s[1] || '').length < prec) {
    s[1] = s[1] || '';
    s[1] += new Array(prec - s[1].length + 1).join('0');
  }
  return s.join(dec);
}


function selectFunction()
{
	var project_id = document.getElementById('project_id').value;
	renderCardsInfo(project_id);
	renderProject(project_id);
	renderPieChart(project_id);
}

$(document).ready(function(){   
	renderCardsInfo(0);
	renderProject(0);
	renderPieChart(0);

});


function renderCardsInfo(project_id)
{
	$.ajax({
	

		url:'/manager-dashboard-cards/' + project_id,
		type:'GET',
		dataType:'json',
success:(data) => {  
	$('#open_tickets').html(JSON.stringify(data.total_open_tickets));

	$('#unassigned_tickets').html(JSON.stringify(data.unassigned_tickets));
	$('#unassinged-progress-bar').remove();
	var unassinged_perc = (data.unassigned_tickets * 100 / data.total_open_tickets) + "%";
	var unassigned_progress_bar = "<div id='unassinged-progress-bar' class='progress-bar bg-warning' role='progressbar' style='width: "+unassinged_perc+"' aria-valuenow='30' aria-valuemin='0' aria-valuemax='100'></div>"
	$('#unassigned_percentage').append(unassigned_progress_bar)

	
	$('#in_progress_tickets').html(JSON.stringify(data.in_progress_tickets));
	$('#in-progress-progress-bar').remove();
	var in_progress_perc = (data.in_progress_tickets * 100 / data.total_open_tickets) + "%";
	var in_progress_progress_bar = "<div id= 'in-progress-progress-bar' class='progress-bar bg-success' role='progressbar' style='width: "+in_progress_perc+"' aria-valuenow='30' aria-valuemin='0' aria-valuemax='100'></div>"
	$('#in_progress_percentage').append(in_progress_progress_bar)

	if (data.avg_time == null)
	{
		var avg_time = '-';
	}
	else
	{
		var avg_time = data.avg_time;
	}
	$('#time_per_ticket').html(avg_time);

}
	});

}

function renderProject(project_id)
{
	$.ajax({
	

		url:'/manager-dashboard/project/' + project_id,
		type:'GET',
		dataType:'json',
success:(data) => {  


	var data_points = 	[]
	var color_buffer = 100 / data.project_list.length
	
	var array_color = ["#b2b266","#4e73df","#ff6666","#d2ff4d","#ffbb33","#adad85"]

	var counter = 0 ;
	for(i in data.project_list)
		{
			var r_quotient = 62 + color_buffer;
			var g_quotient = 28 + color_buffer;
			var b_quotient = 118 + color_buffer;
			var light_color_scheme = "rgba("+r_quotient+" , "+g_quotient+" , "+b_quotient+" , 0)"
			var heavy_color_scheme = array_color[counter]
			var project_data_points = []
			var label_points = []
			for(j=0; j< data.chart_data.length; j++)
			{	
				if(data.chart_data[j].p_id == data.project_list[i].id)
				{
					project_data_points.push(data.chart_data[j].cnt);
					label_points.push(data.chart_data[j].mth_name)
				}
				
			}
			data_points.push({

			  label: data.project_list[i].name,
			  lineTension: 0.3,
			  backgroundColor: light_color_scheme,
			  borderColor: heavy_color_scheme,
			  pointRadius: 3,
			  pointBackgroundColor: heavy_color_scheme,
			  pointBorderColor: heavy_color_scheme,
			  pointHoverRadius: 3,
			  pointHoverBackgroundColor: heavy_color_scheme,
			  pointHoverBorderColor: heavy_color_scheme,
			  pointHitRadius: 10,
			  pointBorderWidth: 2,
			  data: project_data_points,
				
			})

			color_buffer = color_buffer + color_buffer
			counter = counter + 1;
				}
			
	// Area Chart Example
	$('#myAreaChart').remove();
      $('#line-chart').append('<canvas id="myAreaChart"><canvas>');

	var ctx = document.getElementById("myAreaChart");
	var myLineChart = new Chart(ctx, {
	  type: 'line',
	  data: {
		labels: label_points,
		datasets:  data_points
		
		,
	  },

	  options: {
		maintainAspectRatio: false,
		layout: {
		  padding: {
			left: 10,
			right: 25,
			top: 25,
			bottom: 0
		  }
		},
		scales: {
		  xAxes: [{
			time: {
			  unit: 'date'
			},
			scaleLabel: {
				display: true,
				labelString: 'Month'
			  },
			gridLines: {
			  display: false,
			  drawBorder: false
			},
			ticks: {
			  maxTicksLimit: 12
			}
		  }],
		  yAxes: [{
			scaleLabel: {
				display: true,
				labelString: 'Tickets'
			  },
			ticks: {
			  stepSize:5,
			  maxTicksLimit: 5,
			  padding: 10,
			  // Include a dollar sign in the ticks
			  callback: function(value, index, values) {
				return number_format(value);
			  }
			},
			gridLines: {
			  color: "rgb(234, 236, 244)",
			  zeroLineColor: "rgb(234, 236, 244)",
			  drawBorder: false,
			  borderDash: [2],
			  zeroLineBorderDash: [2]
			}
		  }],
		},
		legend: {
		  display: true,
		  position: "bottom"
		},
		tooltips: {
		  backgroundColor: "rgb(255,255,255)",
		  bodyFontColor: "#858796",
		  titleMarginBottom: 10,
		  titleFontColor: '#6e707e',
		  titleFontSize: 14,
		  borderColor: '#dddfeb',
		  borderWidth: 1,
		  xPadding: 15,
		  yPadding: 15,
		  displayColors: false,
		  intersect: false,
		  mode: 'index',
		  caretPadding: 10,
		  callbacks: {
			label: function(tooltipItem, chart) {
			  var datasetLabel = chart.datasets[tooltipItem.datasetIndex].label || '';
			  return datasetLabel + ':' + number_format(tooltipItem.yLabel);
			}
		  }
		}
	  }
	});

}});
}




function renderPieChart(project_id)
{
	
	$.ajax({
	

		url:'/manager-dashboard-piechart/' + project_id,
		type:'GET',
		dataType:'json',
	success:(data) => {  
	
	var label_points = [];
	var data_points = [];
	
	for(i=0 ; i  < data.piechart_data.length; i++)
	{
		label_points.push(data.piechart_data[i].priority);
		data_points.push(data.piechart_data[i].cnt)
	}
	
	// Pie Chart Example
	
	$('#myPieChart').remove();
      $('#pie-chart').append('<canvas id="myPieChart"><canvas>');
	  
var ctx = document.getElementById("myPieChart");
var myPieChart = new Chart(ctx, {
  type: 'doughnut',
  data: {
    labels: label_points,
    datasets: [{
      data: data_points,
      backgroundColor: ['#4e73df', '#ffbb33', '#36b9cc'],
      hoverBackgroundColor: ['#2e59d9', '#17a673', '#2c9faf'],
      hoverBorderColor: "rgba(234, 236, 244, 1)",
    }],
  },
  options: {
    maintainAspectRatio: false,
    tooltips: {
      backgroundColor: "rgb(255,255,255)",
      bodyFontColor: "#858796",
      borderColor: '#dddfeb',
      borderWidth: 1,
      xPadding: 15,
      yPadding: 15,
      displayColors: true,
      caretPadding: 10,
    },
    legend: {

      display: true,
	  position: "bottom"

    },
    cutoutPercentage: 80,
  },
});


}});

}