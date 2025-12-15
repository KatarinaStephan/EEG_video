import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from datetime import timedelta
import scipy.signal as sig
from matplotlib.widgets import Slider


def read_file(filename):
	
	if filename[-4:] == 'xlsx':
		df = pd.read_excel(filename)
	elif filename[-3:] == 'csv':
		df = pd.read_csv(filename)
	else:
		print('File format not recognized')

	return df


def plot_time_slice_raw(time, ch1, ch2, starting_time, filter_bandpass_min=1, filter_bandpass_max=30):

	time_raw = time
	channel1_raw = ch1
	channel2_raw = ch2
	diff_raw = channel2_raw - channel1_raw

	# if using raw dataset, no need to add starting_time_offset
	time_each = time_raw

	# filter raw data using a bandpass with specified bounds
	sos = sig.butter(4, (filter_bandpass_min, filter_bandpass_max), fs=512, btype='bandpass', analog=False, output='sos')
	ch1_filt  = sig.sosfilt(sos, channel1_raw)
	ch2_filt  = sig.sosfilt(sos, channel2_raw)
	diff_filt = sig.sosfilt(sos, diff_raw)

	time_start_s = np.min(time_each) 
	delta_t = np.max(time_each) 

	fig,ax = plt.subplots()
	plt.subplots_adjust(bottom=0.25)

	slider_color = 'White'

	# Set the axis and slider position in the plot
	axis_position = plt.axes([0.2, 0.1, 0.6, 0.03], facecolor = slider_color)
	slider_position = Slider(axis_position, 'Time', time_start_s, time_start_s+delta_t, valinit=time_start_s, valstep=1)

	is_manual = False # True if taken control of the animation
	interval = 100 # ms, time between animation frames
	loop_len = 0.2 # seconds per loop
	scale = interval / 1000 / loop_len

	def update_slider(val):
		global is_manual
		is_manual=True
		update(val)

	def update(val):
		ax.clear()
		t_start = slider_position.val
		t_end = t_start + 30

		offset = 120

		mask1 = (time_each > t_start) & (time_each < t_end)

		ax.plot(time_each[mask1], ch1_filt[mask1] + offset,
		lw=0.8, color='0.4', label='Channel 1')

		ax.plot(time_each[mask1], ch2_filt[mask1],
		lw=0.8, color='0.4', label='Channel 2')

		ax.plot(time_each[mask1], diff_filt[mask1] - offset,
		lw=0.8, color='0.4', label='Difference (Ch2 - Ch1)')

		ax.set_xlim([t_start, t_end])
		ax.set_ylim(-2*offset + 40, 2*offset - 40)
		ax.set_xlabel('TIME (HH:MM:SS)')
		ax.set_ylabel('AMPLITUDE (\u03BCV)')
		ax.set_title('EEG Channels', fontweight='bold', fontsize=18)
		#ax.legend(loc='upper left', fontsize=9, frameon=False)

		# display x-ticks as analog time

		xticks_raw = ax.get_xticks()
		xticks_analog = ['{:s}'.format(str(timedelta(seconds = starting_time + xt))) for xt in xticks_raw]


		ax.set_xticklabels(xticks_analog)

		# display y-ticks from -100 to +100
		yticks = [-offset,0,+offset]
		ytick_labels = ['-100','0','+100']

		ax.set_yticks(yticks)
		ax.set_yticklabels(['Difference', 'Channel 2', 'Channel 1'])


		fig.canvas.draw_idle()


	def update_plot(num):
		global is_manual
		is_manual = False
		if is_manual:
			return ax, # don't change

		val = (slider_position.val + scale) % slider_position.valmax
		slider_position.set_val(val)
		is_manual = False # the above line called update_slider, so we need to reset this
		return ax,

	def on_click(event):
		# Check where the click happened
		(xm,ym),(xM,yM) = slider_position.label.clipbox.get_points()
		if xm < event.x < xM and ym < event.y < yM:
			# Event happened within the slider, ignore since it is handled in update_slider
			return
		else:
			# user clicked somewhere else on canvas = unpause
			global is_manual
			is_manual=False

		

	slider_position.on_changed(update_slider)

	fig.canvas.mpl_connect('button_press_event', on_click)

	ani = animation.FuncAnimation(fig, update_plot, interval=interval)

	plt.show()


	
def main():

	# Raw 
	filename = 'record-[2022.08.22-14.31.58].csv'
	df_raw = read_file(filename)


	time_raw = np.array(df_raw['Time:512Hz'])
	channel1_raw = np.array(df_raw['Channel 1'])
	channel2_raw = np.array(df_raw['Channel 2'])

	# get starting time
	hour, minute, second = 14, 31, 58
	starting_time = (hour*3600+ minute*60+ second)	

	def convert_realtime_to_seconds(h, m, s, starting_time):
		real_time_seconds = h*3600 + m*60 + s	
		return real_time_seconds - starting_time 

		# Subtract the starting time of the raw file so that the time inputted is time after start of raw file
		time_plot_raw = real_time_seconds - starting_time 

		return time_plot_raw

	### MAKE PLOTS ###

	plot_time_slice_raw(time_raw, channel1_raw, channel2_raw,
				starting_time = starting_time,
				filter_bandpass_min = 1,
				filter_bandpass_max = 15)

	plt.show()


### MAIN SCRIPT

if __name__ == "__main__":
	main()