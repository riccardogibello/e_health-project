import os
from matplotlib import pyplot as plt
import seaborn as sns


def save_confusion_matrix(fig_width, fig_height, heatmap_width, heatmap_height, confusion_matrix_dataframe, path):
    plt.figure(figsize=(fig_width, fig_height))
    sns.set(rc={'figure.figsize': (heatmap_width, heatmap_height)})
    # The annot_kws are used to set some properties of the content of each cell in the grid
    sns.heatmap(confusion_matrix_dataframe,
                annot=True,
                annot_kws={'multialignment': 'center', 'verticalalignment': 'center',
                           'horizontalalignment': 'center'},
                linewidths=0.2,
                cbar=True,
                fmt="d")  # cbar set to True in order to have the color map legenda on the right
    # linewidths used to set the spacing in the grid between cells

    plt.title('Confusion Matrix', fontsize='30', fontweight='bold', pad=20)
    plt.ylabel('Actual Values', color='#4cbb17', fontsize='15', labelpad=20)
    plt.xlabel('Predicted Values', color='#1b2ba5', fontsize='15', labelpad=20)

    # Then also the labels are changed in order do be centered although in multiline setting
    locs, labels = plt.xticks()
    plt.xticks(ticks=locs, labels=labels, color='#000000', multialignment='center', verticalalignment='center',
               horizontalalignment='center', fontsize='11')

    locs, labels = plt.yticks()
    plt.yticks(ticks=locs, labels=labels, color='#000000', multialignment='center', verticalalignment='center',
               horizontalalignment='center', fontsize='11')

    plt.tick_params(pad=10)  # this is used to set some padding around the labels on both axes
    if os.path.exists(path):
        os.remove(path)
    plt.savefig(path, bbox_inches='tight')
