import streamlit as st
import pandas as pd
import json
import plotly.express as px


# Load the final results from the JSON file
def load_results():
    try:
        with open("final_results.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        st.error("Final results file not found. Please run the algorithm first.")
        return []


# Prepare data as a DataFrame
def prepare_data(results):
    data = []
    for result in results:
        total_downloads = result["downloads"]  # Ensure consistency of totals per translator
        for post in result["posts"]:
            data.append({
                "Rank": result["rank"],
                "Translator": result["translator"],
                "Total Downloads": total_downloads,
                "Post Title": post["title"],
                "Post Downloads": post["downloads"],
                "PID": post["pid"],
            })
    return pd.DataFrame(data)


# Dashboard layout
def main():
    st.set_page_config(page_title="Trending Translators Dashboard", layout="wide")
    st.title("Trending Translators Dashboard")

    results = load_results()
    if not results:
        return

    df = prepare_data(results)

    # Sidebar: Translator Selection
    st.sidebar.title("Translator Selector")

    # Translator search box
    search_term = st.sidebar.text_input("Search for a Translator")
    translator_table = (
        df.groupby("Translator")[["Rank", "Total Downloads"]]
        .max()
        .reset_index()
        .sort_values("Total Downloads", ascending=False)
    )
    translator_table["Index"] = range(1, len(translator_table) + 1)
    translator_table = translator_table[["Index", "Rank", "Translator", "Total Downloads"]]

    # Add a translator selector dropdown at the top
    translators = translator_table["Translator"].tolist()
    if search_term:
        matching_translators = [t for t in translators if search_term.lower() in t.lower()]
        selected_translator = st.sidebar.selectbox("Matching Translators", options=matching_translators)
    else:
        selected_translator = st.sidebar.selectbox("Select a Translator", options=translators)

    # Sidebar: Translator List
    st.sidebar.write("### Translator List")
    st.sidebar.dataframe(
        translator_table.rename(columns={"Index": "#", "Rank": "Rank", "Translator": "Name", "Total Downloads": "Downloads"}).reset_index(drop=True),
        height=300,
        use_container_width=True,
    )

    # Filter data for the selected translator
    translator_data = df[df["Translator"] == selected_translator].reset_index(drop=True)

    # ** Right Panel: Detailed Analysis **
    if selected_translator:
        col1, col2 = st.columns([1, 3])

        with col1:
            st.write(f"### {selected_translator}'s Overview")
            total_downloads = translator_data["Total Downloads"].iloc[0]
            total_posts = len(translator_data)
            st.metric("Total Downloads", total_downloads)
            st.metric("Number of Posts", total_posts)

        with col2:
            st.write(f"### Download Trends for {selected_translator}")
            # Line Chart: Posts vs. Downloads (Plotly)
            fig = px.line(
                translator_data,
                x="Post Title",
                y="Post Downloads",
                title="Post Downloads Trend",
                labels={"Post Title": "Posts", "Post Downloads": "Downloads"},
            )
            fig.update_layout(xaxis_title="Posts", yaxis_title="Downloads", title_x=0.5)
            fig.update_xaxes(tickangle=45)  # Rotate x-axis labels for readability
            st.plotly_chart(fig, use_container_width=True)

        # ** Visualizations **
        st.write(f"### Post Distribution for {selected_translator}")
        # Bar Chart: Post Distribution
        fig = px.bar(
            translator_data,
            x="Post Title",
            y="Post Downloads",
            text="Post Downloads",
            title="Post Downloads Distribution",
            labels={"Post Title": "Posts", "Post Downloads": "Downloads"},
        )
        fig.update_layout(xaxis_title="Posts", yaxis_title="Downloads", title_x=0.5)
        fig.update_xaxes(tickangle=45)  # Rotate x-axis labels for readability
        st.plotly_chart(fig, use_container_width=True)

        # Post-level Table with an index column
        translator_data["Index"] = range(1, len(translator_data) + 1)
        st.write(f"### Posts by {selected_translator}")
        st.dataframe(
            translator_data[["Index", "Post Title", "Post Downloads", "PID"]]
            .rename(columns={
                "Index": "#",
                "Post Title": "Title",
                "Post Downloads": "Downloads",
                "PID": "Post ID",
            })
            .reset_index(drop=True),
            use_container_width=True,
        )

    # ** Global Insights (Optional Footer) **
    st.write("---")
    st.write("### Global Insights")

    # Deduplicate posts to avoid counting downloads for duplicate posts
    unique_posts = df.drop_duplicates(
        subset=["PID"])  # You can also use ["Post Title", "Post Downloads"] if no unique "PID"
    total_translators = df["Translator"].nunique()
    total_downloads = unique_posts["Post Downloads"].sum()

    st.write(f"**Total Translators**: {total_translators}")
    st.write(f"**Total Downloads Across All Translators**: {total_downloads}")

    st.write(
        """
        #### Tips:
        - Use the sidebar to navigate between translators.
        - Search for translators by name using the search box.
        - Visualize individual translator performance on the right panel.
        """
    )


if __name__ == "__main__":
    main()
