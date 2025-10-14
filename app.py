from datetime import datetime
import streamlit as st
import client


def get_api_key():
    if "api_key" not in st.session_state or not st.session_state.api_key:
        with st.container():
            st.info(
                "Enter your Football API key to use the application. You can get started for free at [API-Football](https://www.api-football.com)."
            )

            api_key = st.text_input(
                "Enter your API key:",
                type="password",
                placeholder="api-sports-key-here",
                key="api_key_input",
            )

            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("Submit", type="primary", use_container_width=True):
                    if api_key:
                        st.session_state.api_key = api_key
                        st.rerun()
                    else:
                        st.error("Please enter a valid API key.")

            st.stop()


def main():
    st.set_page_config(
        page_title="Women's Soccer Stats",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            "Get Help": "mailto:soccer@cantu.dev",
            "Report a bug": "mailto:soccer@cantu.dev",
            "About": f'Built using Streamlit and deployed using Heroku. \nLast deployed on {datetime.now().strftime("%d/%m/%Y at %H:%M:%S UTC")}',
        },
    )

    get_api_key()  # stored in st.session_state.api_key

    st.title("Soccer Stats")
    st.success(f"✅ API Key configured successfully!")
    leagues = client.get_leagues(st.session_state.api_key)
    league_names = [league["league"]["name"] for league in leagues]
    target_league = "NWSL Women"
    nwsl_index = (
        league_names.index(target_league) if target_league in league_names else 0
    )
    selected_league = st.selectbox("Select a League", league_names, index=nwsl_index)
    selected_league_id = next(
        (
            league["league"]["id"]
            for league in leagues
            if league["league"]["name"] == selected_league
        ),
        None,
    )

    data_years = client.get_league_seasons(st.session_state.api_key)
    current_year = datetime.now().year
    # TODO: make this better using the `current` field from the leagues response
    selected_year = st.selectbox(
        "Select a Year",
        sorted(data_years, reverse=True),
        index=data_years.index(current_year) if current_year in data_years else -1,
    )

    teams = client.get_teams(
        st.session_state.api_key, selected_league_id, selected_year
    )
    team_names = [team["team"]["name"] for team in teams]
    selected_team = st.selectbox("Select a Team", team_names)

    selected_team_id = next(
        (team["team"]["id"] for team in teams if team["team"]["name"] == selected_team),
        None,
    )
    players = client.get_team_players(
        st.session_state.api_key, selected_team_id, selected_year
    )
    player_names = [player["player"]["name"] for player in players]
    selected_player = st.selectbox("Select a Player", player_names)

    selected_player_id = next(
        (
            player["player"]["id"]
            for player in players
            if player["player"]["name"] == selected_player
        ),
        None,
    )

    player_stats = client.get_player_stats(
        st.session_state.api_key, selected_player_id, selected_team_id, selected_year
    )

    # TODO: BETTER
    if player_stats:
        st.write(player_stats)


if __name__ == "__main__":
    main()
