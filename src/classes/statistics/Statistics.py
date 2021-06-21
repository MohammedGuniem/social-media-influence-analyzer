import matplotlib.pyplot as plt
import pandas as pd
import datetime
import time
import os


class Statistics:
    def __init__(self, mongo_db_connector, neo4j_db_connector, network_name, submissions_type, date):
        self.network_name = network_name
        self.submissions_type = submissions_type
        self.date = date
        self.mongo_db_connector = mongo_db_connector
        self.neo4j_db_connector = neo4j_db_connector

    def getCrawlingRuntimes(self):
        unix_from_date = time.mktime(datetime.datetime. strptime(
            self.date, '%Y-%m-%d').timetuple())

        runtimes = self.mongo_db_connector.getCrawlingRuntimes(
            self.network_name, self.submissions_type, unix_from_date)

        runtimes_df = pd.DataFrame(runtimes)

        runtimes_df["date"] = pd.to_datetime(
            runtimes_df['timestamp'], unit='s')
        runtimes_df['date'] = pd.to_datetime(
            runtimes_df['date'], format="%d.%m.%y").astype(dtype="string")

        runtimes_df.drop(['timestamp', '_id', 'network_name',
                          'submissions_type'], axis=1, inplace=True)

        runtimes_df["per group"] = runtimes_df["groups_crawling_time"] / \
            runtimes_df["groups_count"]
        runtimes_df["per submission"] = runtimes_df["submissions_crawling_time"] / \
            runtimes_df["submissions_count"]
        runtimes_df["per comment"] = runtimes_df["comments_crawling_time"] / \
            runtimes_df["comments_count"]
        runtimes_df["per training submission"] = runtimes_df["training_submissions_crawling_time"] / \
            runtimes_df["training_submissions_count"]

        # training_submissions_count training_submissions_crawling_time

        runtimes_df.set_index(runtimes_df['date'], inplace=True)
        runtimes_df.rename(
            columns={
                'groups_crawling_time': 'groups',
                'submissions_crawling_time': 'submissions',
                'comments_crawling_time': 'comments',
                'training_submissions_crawling_time': 'training submissions'
            }, inplace=True)

        fig, axes = plt.subplots(1, 2)

        runtimes_df[["date", "per group", "per submission", "per comment", "per training submission"]].plot(
            kind="bar", stacked=True, ax=axes[0], rot='horizontal', fontsize=8, title="Average Crawling runtimes").set(ylabel='seconds')

        runtimes_df[["date", "groups", "submissions", "comments", "training submissions"]].plot(
            kind="bar", stacked=True, ax=axes[1], rot='horizontal', fontsize=8, title="Total Crawling runtimes").set(ylabel='seconds')

        fig.suptitle('Crawling Runtimes Statistics')

        path = F"{os.getcwd()}/statistics_plots/crawling/{self.network_name}/{self.date}/{self.submissions_type}/"
        self.create_directory_if_not_found(
            path=path)
        plot_img_name = F"crawling_bar_plot.jpg"
        fig.set_size_inches(15, 10)
        plt.savefig(
            F"{path}{plot_img_name}", format="jpg", dpi=500)

    def getInfluenceArea(self):
        groups = self.mongo_db_connector.getGroups(
            self.network_name, self.submissions_type)

        submissions = []
        for group in groups:
            group_submissions = self.mongo_db_connector.getSubmissionsOnGroup(
                self.network_name, self.submissions_type, group['id'])
            submissions += group_submissions

        groups_df = pd.DataFrame(groups).rename(
            columns={'id': 'group_id'}).drop(['_id'], axis=1)

        submissions_df = pd.DataFrame(submissions).drop(['_id'], axis=1)

        submissions_df = pd.merge(submissions_df, groups_df,
                                  how='outer', on=['group_id'])

        fig, axes = plt.subplots(1, 3)

        submissions_df.groupby("display_name")["display_name"].count().plot(
            kind="pie", ax=axes[0], title="Crawled Groups", autopct='%1.1f%%').axis("off")

        neo4j_graph, centralities_max = self.neo4j_db_connector.get_graph(
            network_name=self.network_name, submissions_type=self.submissions_type, date=self.date, relation_type="Influences")

        groups = []
        predicted_influence = []
        for link in neo4j_graph["links"]:
            predicted_influence += link["props"]["influence_areas"]
            groups += link["props"]["groups"]

        groups_df = pd.DataFrame(
            groups, columns=["groups"])

        groups_df.groupby("groups")[
            "groups"].count().plot(kind="pie", ax=axes[1], title="Modelled Groups", autopct='%1.1f%%').axis("off")

        predicted_influence_df = pd.DataFrame(
            predicted_influence, columns=["predicted_influence"])

        predicted_influence_df.groupby("predicted_influence")[
            "predicted_influence"].count().plot(kind="pie", ax=axes[2], title="Predicted Influence Areas", autopct='%1.1f%%').axis("off")

        fig.suptitle(
            'Crawled Subreddits vs. Predicted Influence Area vs. Modelled Subreddits')

        path = F"{os.getcwd()}/statistics_plots/influence_areas_and_subreddits/{self.network_name}/{self.date}/{self.submissions_type}/"
        self.create_directory_if_not_found(
            path=path)
        plot_img_name = F"topics_and_subreddits_pie_plot.jpg"

        fig.set_size_inches(15, 10)
        plt.savefig(
            F"{path}{plot_img_name}", format="jpg", dpi=500)

    def getInfluenceScore(self, score_type):
        neo4j_graph, centralities_max = self.neo4j_db_connector.get_graph(
            network_name=self.network_name, submissions_type=self.submissions_type, date=self.date, relation_type="Influences")

        if score_type:
            request_score_type = score_type
        else:
            request_score_type = "all_scores"

        if score_type == "single_scores":
            score_types = ["interaction", "activity", "upvotes"]
        elif score_type == "dobble_scores":
            score_types = ["interaction_and_activity",
                           "activity_and_upvotes", "interaction_and_upvotes"]
        elif score_type:
            score_types = [score_type]
            #fig, axes = plt.subplots(2, 1)
            #fig.suptitle(F"Influence Scores Distribution using {score_type}")
        else:
            score_types = ["interaction", "activity", "upvotes", "interaction_and_activity",
                           "activity_and_upvotes", "interaction_and_upvotes", "total"]

        fig, axes = plt.subplots(2, len(score_types), figsize=(24, 10))
        fig.tight_layout(pad=4.0)
        fig.suptitle("Influence Scores Distribution")

        axes = axes.ravel()

        links = {}
        for score_type in score_types:
            links[F"{score_type}"] = []
            for link in neo4j_graph["links"]:
                links[F"{score_type}"].append(link['props'][F"{score_type}"])

        links_df = pd.DataFrame(links)

        for score_type in score_types:
            links_df[F"{score_type}"].plot(
                kind="box",
                ax=axes[score_types.index(score_type)],
                title=F"{score_type.replace('_', ' ')}",
                vert=False
            )
            y_axis = axes[score_types.index(score_type)].axes.get_yaxis()
            y_axis.set_visible(False)

            links_df[F"{score_type}"].plot(
                kind="hist",
                bins=links_df[F"{score_type}"].nunique(),
                ax=axes[score_types.index(score_type)+len(score_types)],
                title=F"{score_type.replace('_', ' ')}",
                xticks=links_df[F"{score_type}"],
                rot=90
            )

        path = F"{os.getcwd()}/statistics_plots/influence_scores/{self.network_name}/{self.date}/{self.submissions_type}/"
        self.create_directory_if_not_found(
            path=path)
        plot_img_name = F"scores_box_plot_{request_score_type}.jpg"
        fig.set_size_inches(15, 10)
        plt.savefig(
            F"{path}{plot_img_name}", format="jpg", dpi=500)
        plt.close('all')

    def create_directory_if_not_found(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
