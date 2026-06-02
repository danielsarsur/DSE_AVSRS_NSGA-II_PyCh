from matplotlib import pyplot as plt
import matplotlib
matplotlib.use('nbagg')

# =================================
# Code for drawing lot-time diagrams
# =================================
def draw_lot_time_diagram(locations, lots):
    fig, ax = plt.subplots()
    
    # Set colors
    prop_cycle = plt.rcParams['axes.prop_cycle']
    colors = prop_cycle.by_key()['color']
    location_colors_dict = {}
    for j, loc in enumerate(locations):
        location_colors_dict[loc] = colors[j]

    # Create plot
    lot_labels = []
    yticks = []
    for i, lot in enumerate(lots):
        xranges = []
        for j, loc in enumerate(locations):
            if loc in lot:
                timings = lot[loc]
                xrange = (timings[0], timings[1]-timings[0])
            else:
                xrange = (-1,-1)
            xranges.append(xrange)
        
        ax.broken_barh(xranges, (-10*i, 10), facecolors=colors, edgecolor= 'k')
        lot_labels.append(f"lot {i}")
        yticks.append(i*-10+5)
    
    # Create legend
    labels = locations
    handles = [plt.Rectangle((0,0),1,1, color=location_colors_dict[label]) for label in labels]
    plt.legend(handles, labels)

    # Create Y and X labels
    ax.set_xlim(left=0)
    ax.set_yticks(yticks)
    ax.set_yticklabels(lot_labels)
    ax.set_xlabel('seconds since start')
    plt.show()
