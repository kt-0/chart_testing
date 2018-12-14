from charts.models import Chart, Label, BackgroundColor, BorderColor, Dataset, Data
from django.db import models
import pandas as pd
import datetime, math, praw, random, os, requests
import itertools

# TODO:
#	(1): Add min and max datasets to line_chart which sit on the same graph but
#		 are simply points instead of connecting lines
#	(2): refactor the way chart objects and their child sets are created or updated

#df1 = pd.read_excel("/Users/kjt/Desktop/front_page/assets/front_page_data_2.xlsx", "Sheet1")
#df1.to_csv("/Users/kjt/Desktop/front_page/assets/front_page_data_2.csv")
#set dtypes here,
#dtype={}

# file location for use on macbook
#df1 = pd.read_csv("/Users/kjt/Desktop/front_page/assets/front_page_data_2.csv", dtype={'Submission_ID':str, 'Score':int, 'Subreddit':str, 'Author': str, 'Rank':int, 'short_link': str}, index_col=0)

# for use with pi
df1 = pd.read_csv("../static/misc/front_page_data_2.csv", dtype={'Submission_ID':str, 'Score':int, 'Subreddit':str, 'Author': str, 'Rank':int, 'short_link': str}, index_col=0)

GR8_25 = (lambda x: x>25)
LESS_25 = (lambda x: x<26)

def update_charts():

	# necessary in order for initial migrations to run properly
	try:
		dt1 = datetime.datetime.now() - datetime.timedelta(days=1)
		dt2 = dt1 - datetime.timedelta(days=31)
		end_date = dt1.strftime("%m/%d/%y %H:%M:%S")
		start_date = dt2.strftime("%m/%d/%y %H:%M:%S")

		df_id = df1[(df1['time_stamp'] > start_date) & (df1['time_stamp'] <= end_date) & (df1['Rank'] < 26)]
		id_list = list(set(df_id["Submission_ID"].tolist()))

		ind = pd.date_range(start='00:00:00', freq='5min', name='time', periods=25).time
		df = pd.DataFrame( {'time': ind} )

		for post_id in id_list:
			df2 = df1.loc[df1.Submission_ID == post_id, ['Rank','Score']]
			frontP_tupp = list(drop_take(df2.iterrows()))
			df_temp = pd.DataFrame( {'Score':[y for x,y in frontP_tupp]})

			df[post_id] = df_temp['Score'].pct_change()

		df.iloc[0, 1:] = 0
		threshold = math.floor((df.shape[1]-2)*.25)
		print("threshold: ", threshold)
		df_copy = df.copy()
		df['average'] = df_copy.mean(numeric_only=True, axis=1)
		#print(df['average'])
		time_list = list(map(lambda x: str(x), ind))
		data_values = list(map(lambda x: round(x*100, 1), df['average'].tolist()))

		chart_dict = {"placeholder":"bar", "waddup":"doughnut", "butthole":"polarArea", "average_monthly_increase":"line", "num_front_posts":"bar"}
		bgcolor_list = {
			'red': 'rgba(255, 99, 132, 0.5)',
			'blue': 'rgba(54, 162, 235, 0.5)',
			'yellow': 'rgba(255, 206, 86, 0.5)',
			'dark-green': 'rgba(51, 102, 0, 0.5)',
			'purple': 'rgba(153, 102, 255, 0.5)',
			'orange': 'rgba(255, 159, 64, 0.5)',
			'teal': 'rgba(75, 192, 192, 0.5)',
			'lavendar': 'rgba(102, 102, 255, 0.5)',

			}

		# iterator for generating colors
		color_loop = itertools.cycle(bgcolor_list.items())
		count = 1
		for x,y in chart_dict.items():
			chart,created = Chart.objects.get_or_create(
				name=x, chart_type=y,
				defaults={'chart_type':y},
			)

			print("chart name: ", chart.name)
			print("chart pk: ", chart.pk)

			# the first 3 charts are random
			if (count < 4):
				num_datas = random.randint(3,7)

				chart.backgroundcolor_set.all().delete()
				chart.label_set.all().delete()
				chart.data_set.all().delete()

				for x in range(num_datas):
					key = next(color_loop)
					chart.label_set.add(Label(name=key[0]), bulk=False)
					chart.data_set.add(Data(value=random.randint(5,30)), bulk=False)
					chart.backgroundcolor_set.add(BackgroundColor(value=key[1]), bulk=False)


			count = count+1
			print('count: ', count)

			if chart.name is 'average_monthly_increase':
				if not created:
					main_tup = list(zip(time_list, data_values, chart.label_set.all(), chart.data_set.all()))
					for a,b,x,y in main_tup:
						Label.objects.filter(pk=x.pk).update(name=a)
						Data.objects.filter(pk=y.pk).update(value=b)

				else:
					label_and_data = list(zip(time_list,data_values))
					for x,y in label_and_data:
						chart.label_set.add(Label(name=x), bulk=False)
						chart.data_set.add(Data(value=y), bulk=False)

			if chart.name is 'num_front_posts':
				df2 = df_id.sort_values(by='Score', ascending=False).drop_duplicates('Submission_ID', keep='last').groupby('Subreddit').agg({'Subreddit':"count"}).sort_values(by='Subreddit', ascending=False)
				sub_list = []
				data_list = []
				for x,y in df2.iloc[:15, :].itertuples():
					sub_list.append(x)
					data_list.append(y)

				sub_list.append('Other')
				data_list.append(float(df2['Subreddit'][df2['Subreddit'] > 1].iloc[16:32].sum()))

				if created:

					top_sixteen = list(zip(sub_list, data_list))

					for x,y in top_sixteen:

						key = next(color_loop)
						chart.backgroundcolor_set.add(BackgroundColor(value=key[1]), bulk=False)
						chart.label_set.add(Label(name=x), bulk=False)
						chart.data_set.add(Data(value=y), bulk=False)

				else:
					# update existing entries
					big_daddy_tup = list(zip(sub_list, data_list, chart.label_set.all(), chart.data_set.all()))
					for a,b,x,y in big_daddy_tup:
						Label.objects.filter(pk=x.pk).update(name=a)
						Data.objects.filter(pk=y.pk).update(value=b)
	except:
		print("Encountered exception in db_updater.py")
	# for chart in charts:
	# 	ch = Chart.objects.get(name=chart.name)
	# 	for d in ch.data_set.all():
	# 		# these values should be pulled from pandas dataframe
	# 		d.value += 1
	# 		d.save()

# takes a post_id, gets 2col dataframe containing consecutive front_page time,
# returns 1col dataframe containing the perc increase per each 5min interval.
# NOTE: Could likely shorten the code with less variables, but it would start to look
# shitty/unreadable
def get_perc_inc(post_id):

	df2 = df1.loc[df1.Submission_ID == post_id, ['Rank','Score']]
	frontP_tupp = list(drop_take(df2.iterrows()))

	#df3 = pd.DataFrame( { 'Rank':[x for x,y in frontP_tupp] ,'Score': [y for x,y in frontP_tupp]})
	#return pd.DataFrame( { post_id: df3['Score'].pct_change() })

	return pd.DataFrame( {'Score':[y for x,y in frontP_tupp]})


def drop_take(iterable):
	for x in iterable:
		next_item = next(iterable)
		next_rank, next_score = next_item[1][0], next_item[1][1]
		if ((LESS_25(x[1][0])) or (LESS_25(next_rank))):
			yield (x[1][0], x[1][1])
			yield (next_rank, next_score)
			break
	for x in iterable:
		if LESS_25(x[1][0]):
			yield (x[1][0],x[1][1])
		else:
			yield (x[1][0], x[1][1])			# this additional yield makes the generator grab one extra at the end
			break

def color_wheel(n=1):
	bgcolor_list = {
		'red': 'rgba(255, 99, 132, 0.5)',
		'blue': 'rgba(54, 162, 235, 0.5)',
		'yellow': 'rgba(255, 206, 86, 0.5)',
		'dark-green': 'rgba(51, 102, 0, 0.5)',
		'purple': 'rgba(153, 102, 255, 0.5)',
		'orange': 'rgba(255, 159, 64, 0.5)',
		'teal': 'rgba(75, 192, 192, 0.5)',
		'lavendar': 'rgba(102, 102, 255, 0.5)',
		}

	# iterator for generating colors
	color_loop = itertools.cycle(bgcolor_list.items())
	color_list = []
	for _ in range(n):
		color = next(color_loop)
		color_list.append((color[0],color[1]))

	return color_list


# creates new charts
def create_new(n=0):
	chart_list = ["bar", "doughnut", "polarArea", "line", "bar"]
	num_charts = n or random.randint(3,5)
	for _ in range(num_charts):
		chart_type = random.choice(chart_list)
		chart_list.pop(chart_list.index(chart_type))
		name = requests.get('https://makemeapassword.org/api/v1/passphrase/plain?wc=1').text
		chart,created = Chart.objects.get_or_create(
			name=name, chart_type=chart_type,
			defaults={'chart_type':chart_type},
		)
		num_datas = random.randint(3,7)
		colors = color_wheel(num_datas)
		for x in colors:
			chart.label_set.add(Label(name=x[0]), bulk=False)
			chart.data_set.add(Data(value=random.randint(5,30)), bulk=False)
			chart.backgroundcolor_set.add(BackgroundColor(value=x[1]), bulk=False)

if __name__ == "__main__":
	main()
