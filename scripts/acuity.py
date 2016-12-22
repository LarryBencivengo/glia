import glia
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from functools import update_wrapper, partial

# def plot_motion_sensitivity(axis_gen,data):
def c_plot_bar(ax, title):
    # continuation
    ax.set_title(title)
    ax.set_xlabel("time (s)")
    ax.set_ylabel("trials by descending bar width")

def plot_solid_versus_bar(axis_gen,data, prepend, append):
    solids,bars_by_speed = data
    for speed in sorted(list(bars_by_speed.keys())):
        bars = bars_by_speed[speed]
        max_lifespan = max(bars,
            key=lambda e: e["stimulus"]["lifespan"])["stimulus"]["lifespan"]/120
        lifespans = set()
        for e in bars:
            # need to calculate duration of light over a particular point
            width = e["stimulus"]["width"]
            light_duration = int(np.ceil(width/speed*120))
            lifespans.add(light_duration)

        light_wedge = glia.compose(
            partial(filter,lambda x: x["stimulus"]["lifespan"] in lifespans),
            partial(sorted,key=lambda x: x["stimulus"]["lifespan"])
        )
        
        sorted_solids = light_wedge(solids)
        sorted_bars = sorted(bars,key=lambda x: x["stimulus"]["width"])


        xlim = glia.axis_continuation(lambda axis: axis.set_xlim(0,max_lifespan))
        bar_text = glia.axis_continuation(partial(c_plot_bar,
            title="Bars with speed: {}".format(speed)))

        glia.plot_spike_trains(axis_gen,sorted_solids,prepend,append,continuation=xlim)
        glia.plot_spike_trains(axis_gen,sorted_bars,
            continuation=glia.compose(xlim,bar_text))

# for v2
def plot_solid_versus_bar_for_speed(axis_gen,data, prepend, append, speed):
    # also assumes 5 contrasts
    solids,bars_by_speed = data
    bars = bars_by_speed[speed]
    max_lifespan = max(bars,
        key=lambda e: e["stimulus"]["lifespan"])["stimulus"]["lifespan"]/120
    lifespans = set()
    colors = set()
    for e in bars:
        # need to calculate duration of light over a particular point
        width = e["stimulus"]["width"]
        color = e["stimulus"]["barColor"]
        light_duration = int(np.ceil(width/speed*120))
        lifespans.add(light_duration)
        colors.add(color)

    xlim = glia.axis_continuation(lambda axis: axis.set_xlim(0,max_lifespan))
    color_text = lambda x: glia.axis_continuation(partial(c_plot_bar,
            title="Color: {}".format(x)))
    plot_continuation = lambda x: glia.compose(xlim,color_text(x))
    sorted_colors = sorted(list(colors),reverse=True)

    # we plot the solid first so they are all on the same row
    for color in sorted_colors:
        light_wedge = glia.compose(
            partial(filter,lambda x: x["stimulus"]["lifespan"] in lifespans),
            partial(filter,lambda x: x["stimulus"]["backgroundColor"]==color),
            partial(sorted,key=lambda x: x["stimulus"]["lifespan"])
        )
        
        sorted_solids = light_wedge(solids)
        glia.plot_spike_trains(axis_gen,sorted_solids,prepend,append,
            continuation=plot_continuation(color))

    for color in sorted_colors:
        filtered_bars = glia.compose(
            partial(filter,lambda x: x["stimulus"]["barColor"]==color),
            partial(sorted,key=lambda x: x["stimulus"]["width"])
            )
        sorted_bars = filtered_bars(bars)
        glia.plot_spike_trains(axis_gen,sorted_bars,
            continuation=xlim)

def plot_motion_sensitivity(axis_gen,data,nwidths,speeds,prepend, append):
    solids,bars_by_speed = data    
    # We assume each band of widths is length 8 & first band is 2-16
    # each subsequent band is twice the width
    
    # the list is sorted so the final bar has longest lifespan
    max_lifespan = bars_by_speed[speeds[0]][nwidths-1]["stimulus"]["lifespan"]/120
    
    for i,speed in enumerate(speeds):
        base_width = 2**(i+1)
        next_width = base_width
        widths = {base_width*(n+1) for n in range(8)}
        bars_to_plot = list(filter(lambda x: x["stimulus"]["width"] in widths,
            bars_by_speed[speed]))
        bars_to_plot.sort(key=lambda x: x["stimulus"]["width"])
        try:
            assert len(bars_to_plot)==8
        except:
            print("width",widths)
            print([bar["stimulus"] for bar in bars_to_plot])
            raise

        xlim = glia.axis_continuation(lambda axis: axis.set_xlim(0,max_lifespan))
        ylim = glia.axis_continuation(lambda axis: axis.set_ylim(0,8))
        bar_text = glia.axis_continuation(partial(c_plot_bar,
            title="Bars with speed: {} & base width: {}".format(
                speed,base_width)))
        glia.plot_spike_trains(axis_gen,bars_to_plot,
            continuation=glia.compose(xlim,bar_text,ylim))
        
        if i==len(speeds)-1:
            # After the last speed, Plot solid
            lifespans = set()
            for w in widths:
                light_duration = int(np.ceil(w/speed*120))
                lifespans.add(light_duration)
                
            light_wedge = glia.compose(
                partial(filter,lambda x: x["stimulus"]["lifespan"] in lifespans),
                partial(sorted,key=lambda x: x["stimulus"]["lifespan"])
            )
            
            sorted_solids = light_wedge(solids)
            glia.plot_spike_trains(axis_gen,sorted_solids,prepend,append,continuation=xlim)
 

def save_acuity_chart(units, stimulus_list, c_add_unit_figures,
                      c_add_retina_figure, prepend, append):
    "Compare SOLID light wedge to BAR response in corresponding ascending width."

    print("Creating acuity chart.")
    # for each speed, create two charts--SOLID & BAR
    # the solid should only include lifespans corresponding to each width

    # pseudocode
    # create dictionary of speeds
    # for each speed:
    #     lifespans = widths["lifespan"]
    #     f_select_experiments(widths)
    #     solids = f_select(solid like spent)
    #     plot_solid_wedge(solids)
    #     plot_spike_trains(solids)

    get_solids = glia.compose(
        glia.f_create_experiments(stimulus_list,prepend_start_time=prepend,
                                  append_lifespan=append),
        glia.f_has_stimulus_type(["SOLID"]),
    )
    solids = glia.apply_pipeline(get_solids,units)

    get_bars_by_speed = glia.compose(
        glia.f_create_experiments(stimulus_list),
        glia.f_has_stimulus_type(["BAR"]),
        partial(glia.group_by,key=lambda x: x["stimulus"]["speed"])
    )
    bars_by_speed = glia.apply_pipeline(get_bars_by_speed,units)

    nspeeds = len(glia.get_unit(bars_by_speed)[1].keys())
    sm_speeds = [60,120,240]
    sm_nspeeds = len(sm_speeds)

    # we plot bar and solid for each speed
    plot_function = partial(plot_solid_versus_bar,prepend=prepend,append=append)
    result = glia.plot_units(plot_function,solids,bars_by_speed,
                             nplots=nspeeds*2,ncols=2,ax_xsize=10, ax_ysize=5)
    c_add_unit_figures(result)
    glia.close_figs([fig for the_id,fig in result])
    
    # now plot the spatial/motion test
    plot_function = partial(plot_motion_sensitivity,prepend=prepend,append=append,
        nwidths=8,speeds=sm_speeds)
    result = glia.plot_units(plot_function,solids,bars_by_speed,
                nplots=sm_nspeeds+1,ncols=4,
                ax_xsize=10, ax_ysize=5,
                figure_title="Spatial/Motion test - each chart has the same light duration")
    c_add_unit_figures(result)
    glia.close_figs([fig for the_id,fig in result])


def save_acuity_chart_v2(units, stimulus_list, c_add_unit_figures,
                      c_add_retina_figure, prepend, append):
    "Compare SOLID light wedge to BAR response in corresponding ascending width."

    print("Creating acuity chart.")
    # for each speed, create two charts--SOLID & BAR
    # the solid should only include lifespans corresponding to each width

    # pseudocode
    # create dictionary of speeds
    # for each speed:
    #     lifespans = widths["lifespan"]
    #     f_select_experiments(widths)
    #     solids = f_select(solid like spent)
    #     plot_solid_wedge(solids)
    #     plot_spike_trains(solids)

    get_solids = glia.compose(
        glia.f_create_experiments(stimulus_list,prepend_start_time=prepend,
                                  append_lifespan=append),
        glia.f_has_stimulus_type(["SOLID"]),
    )
    solids = glia.apply_pipeline(get_solids,units)

    get_bars_by_speed = glia.compose(
        glia.f_create_experiments(stimulus_list),
        glia.f_has_stimulus_type(["BAR"]),
        partial(glia.group_by,key=lambda x: x["stimulus"]["speed"])
    )
    bars_by_speed = glia.apply_pipeline(get_bars_by_speed,units)

    speeds = list(glia.get_unit(bars_by_speed)[1].keys())
    nspeeds = len(speeds)
    colors = set()
    for solid in glia.get_unit(solids)[1]:
        colors.add(solid["stimulus"]["backgroundColor"])
    ncolors = len(colors)
    # sm_speeds = [60,120,240]
    # sm_nspeeds = len(sm_speeds)

    # we plot bar and solid for each speed and each of 5 colors
    for speed in sorted(speeds):
        plot_function = partial(plot_solid_versus_bar_for_speed,
                            prepend=prepend,append=append,speed=speed)
        result = glia.plot_units(plot_function,solids,bars_by_speed,
                                 nplots=nspeeds*2*ncolors,ncols=ncolors,ax_xsize=10, ax_ysize=5,
                                 figure_title="Top: Solid, Bottom: Bars with speed {}".format(speed))
        c_add_unit_figures(result)
        glia.close_figs([fig for the_id,fig in result])
    
    # # now plot the spatial/motion test
    # plot_function = partial(plot_motion_sensitivity,prepend=prepend,append=append,
    #     nwidths=8,speeds=sm_speeds)
    # result = glia.plot_units(plot_function,solids,bars_by_speed,
    #             nplots=sm_nspeeds+1,ncols=4,
    #             ax_xsize=10, ax_ysize=5,
    #             figure_title="Spatial/Motion test - each chart has the same light duration")
    # c_add_unit_figures(result)
    # glia.close_figs([fig for the_id,fig in result])

