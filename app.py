from flask import Flask, render_template, request
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.utils
import json

app = Flask(__name__)

# Sample questions and answers - replace with your full list
QUESTIONS_AND_ANSWERS = {
    "Q1": {
        "text": "How many Brunos would you need to measure the height of the Statue of Liberty?",
        "answer": 52
    },
    "Q2": {
        "text": "What is the area, in square feet, of UC Berkeley's main campus?",
        "answer": 7753680
    },
    "Q3": {
        "text": "In 2023 specifically, how many employees did the Blue Chip company with headquarters closest to Berkeley have?",
        "answer": 45600
    },
    "Q4": {
        "text": "How many career receiving yards do Christian McCaffrey, Deebo Samuel Sr., and Brock Purdy have combined?",
        "answer": 9258
    },
    "Q5": {
        "text": "How many pounds of marijuana were seized by U.S. Border Patrol in fiscal year 2023?",
        "answer": 42314
    },
    "Q6": {
        "text": "How many people, in total, attended the 2010 FIFA World Cup in South Africa?",
        "answer": 3178856
    },
    "Q7": {
        "text": "How much time, in minutes, would a flight going from Boston to Barcelona to Beijing to Bangkok to Busan spend in the air?",
        "answer": 1725
    },
    "Q8": {
        "text": "How much money, in quarters, would you have needed to buy 10,000 shares of Microsoft on the day of its IPO back in 1986?",
        "answer": 840000
    },
    "Q9": {
        "text": "On average, how many gallons of crude oil did Venezuela export per day in 2014?",
        "answer": 1964861
    },
    "Q10": {
        "text": "How long would it take someone, in seconds, to run from Berkeley, CA to Stanford, CA if they ran at Usain Bolt's fastest recorded speed?",
        "answer": 5441
    },
    "Q11": {
        "text": "If you were to take the AUM of Citadel at the beginning of 2025 and convert it to one-dollar bills, how many American football fields long would that stack of bills be?",
        "answer": 64699
    },
    "Q12": {
        "text": "How many free throws has Steph Curry missed in his entire career to date?",
        "answer": 385
    },
    "Q13": {
        "text": "What is the total number of characters (punctuation and spacing included) of every movie title in IMDB's top 250?",
        "answer": 4070
    }
}

num_questions = 13

def calculate_interval_score(lower, upper, true_answer):
    """Calculate if an interval is correct and its score contribution"""
    if lower <= true_answer <= upper:
        return True, upper/lower
    return False, 0

def calculate_team_score(row):
    """Calculate the total score for a team"""
    good_intervals = 0
    ratio_sum = 0
    
    for q_num in range(1, num_questions + 1):
        lower = row[f'Q{q_num}. Lower Bound']
        upper = row[f'Q{q_num}. Upper Bound']
        true_answer = QUESTIONS_AND_ANSWERS.get(f'Q{q_num}', {}).get('answer', 0)
        
        is_good, ratio = calculate_interval_score(lower, upper, true_answer)
        if is_good:
            good_intervals += 1
            ratio_sum += ratio
    
    return (10 + ratio_sum) * (2 ** (num_questions - good_intervals))

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Handle file upload
        file = request.files['file']
        if file:
            df = pd.read_csv(file)
            
            # Calculate scores for each team
            results = []
            for _, row in df.iterrows():
                team_name = row['Team Name']
                score = calculate_team_score(row)
                
                # Calculate per-question results
                question_results = []
                for q_num in range(1, num_questions + 1):
                    lower = row[f'Q{q_num}. Lower Bound']
                    upper = row[f'Q{q_num}. Upper Bound']
                    true_answer = QUESTIONS_AND_ANSWERS.get(f'Q{q_num}', {}).get('answer', 0)
                    is_good, ratio = calculate_interval_score(lower, upper, true_answer)
                    
                    question_results.append({
                        'question': q_num,
                        'lower': lower,
                        'upper': upper,
                        'correct': is_good,
                        'ratio': ratio if is_good else 0
                    })
                
                results.append({
                    'team': team_name,
                    'score': score,
                    'questions': question_results
                })
            
            # Sort results by score (ascending)
            results.sort(key=lambda x: x['score'])
            
            # Create leaderboard visualization
            fig_leaderboard = go.Figure(data=[
                go.Bar(
                    x=[r['team'] for r in results],
                    y=[r['score'] for r in results],
                    text=[f"{r['score']:.2f}" for r in results],
                    textposition='auto',
                )
            ])
            fig_leaderboard.update_layout(
                title='Team Scores (Lower is Better)',
                xaxis_title='Team',
                yaxis_title='Score'
            )
            leaderboard_json = json.dumps(fig_leaderboard, cls=plotly.utils.PlotlyJSONEncoder)
            
            return render_template('results.html', 
                                results=results,
                                questions=QUESTIONS_AND_ANSWERS,
                                leaderboard_plot=leaderboard_json)
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)