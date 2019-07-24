import re
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

pre_char = {}
next_char = {}

letters = [chr(i) for i in range(97, 123)]


def init_counter():
    for letter in letters:
        pre_char[letter] = dict(zip(letters, [0 for i in range(26)]))
        next_char[letter] = dict(zip(letters, [0 for i in range(26)]))


def uniform_pinyin(pinyins):
    pinyins = re.sub("[{}]".format("āáǎàɑ"), "a", pinyins)
    pinyins = re.sub("[{}]".format("ōóǒòó̀"), "o", pinyins)
    pinyins = re.sub("[{}]".format("ūúǔù"), "u", pinyins)
    pinyins = re.sub("(?<=[ln])[{}](?=[e\s])".format("üǖǘǚǜ"), "v", pinyins)
    pinyins = re.sub("[{}]".format("üǖǘǚǜ"), "u", pinyins)
    pinyins = re.sub("[{}]".format("īíǐì"), "i", pinyins)
    pinyins = re.sub("[{}]".format("ēéěè"), "e", pinyins)
    pinyins = re.sub("[{}]".format("ńňǹ"), "n", pinyins)
    pinyins = re.sub("[{}]".format(",ḿ"), "", pinyins)
    pinyins = re.sub("[{}]".format("ɡ"), "g", pinyins)
    return pinyins


def purify_pinyin(pinyins, blank=1, lower_case=1):
    pinyins = uniform_pinyin(pinyins)
    pinyins = pinyins.lower()
    pinyins = re.sub(r'[^a-z]', " ", pinyins)
    pinyins = re.sub(r'\s+', " ", pinyins)
    return pinyins


def count_neighbour(file):
    init_counter()
    with open(file, 'r', encoding="utf-8") as fp:
        msg = purify_pinyin(fp.read())
    for i, j in pre_char.items():
        for x in re.finditer(i, msg):
            # print(x.span())
            if x.span()[1] < len(msg) and msg[x.span()[1]].strip():
                next_char[i][msg[x.span()[1]]] += 1
            if x.span()[0] > 0 and msg[x.span()[0] - 1].strip():
                pre_char[i][msg[x.span()[0] - 1]] += 1


def plot_neneighbour(file, forward=0, pct=0):
    fname = file[:-4].replace("_op", "")
    fig_title = fname + "-"
    if forward == 1:
        fig_title += "后方字母"
        src = next_char
    else:
        fig_title += "前方字母"
        src = pre_char
    tally = pd.DataFrame(src)
    print(tally)
    if re.search("已加密", file):
        tally.rename(columns=lambda x: x.upper(),
                     index=lambda x: x.upper(), inplace=True)
    prob = tally.div(tally.sum(axis=0), axis=1).fillna(0).round(2)
    if pct == 1:
        fig_title += "概率"
        data = prob
        color_cfg = "RdYlGn_r"
        fmt_cfg = ".2f"
    else:
        fig_title += "计数"
        data = tally
        color_cfg = "coolwarm"
        fmt_cfg = "d"
    plt.rcParams['font.size'] = 11
    plt.rcParams['font.sans-serif'] = ['SimHei']
    fig, ax = plt.subplots(figsize=(14, 8))
    plt.subplots_adjust(left=0.02, right=1, top=0.93,
                        bottom=0, wspace=0.03, hspace=0.02)  # 调整子图间距
    sns.heatmap(data, ax=ax, annot=True, fmt=fmt_cfg,
                cmap=color_cfg, cbar=False)
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=12)
    ax.xaxis.tick_top()
    ax.axes.set_title(fig_title, fontsize=12, y=1.01)
    # plt.savefig(fig_title + r'.pdf', format='pdf')
    plt.savefig(fig_title + r'.svg', format='svg')
    # plt.savefig(fig_title + r'.png', format='png')
    plt.show()


def main(file):
    count_neighbour(file)
    plot_neneighbour(file)
    plot_neneighbour(file, forward=1, pct=0)
    if not re.search("已加密", file):
        plot_neneighbour(file, forward=0, pct=1)
        plot_neneighbour(file, forward=1, pct=1)

if __name__ == '__main__':
    main("all_pinyin.txt")
