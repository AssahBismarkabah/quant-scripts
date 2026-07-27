### **three parameters**

- Entry Logic clearly defined with no ambiguity that it can be used by someone or implemented by a machine(exact something a machine can execute on every single bar when the conditions are met)
- Exit Logic(Stop Loss, Take profit, and a condition when none of those are met)
- Position sizing(how much do we want to Risk)
- The why? who is in the other side of this trade and why are they statistically giving you money(a clear reason on why a specific behavior in the market is giving you an edge, who is on the other side of the trade and why are they systematically giving you money, e.g let say you know that every 2:00pm crypto funds are going to buy or sell to rebalance their portfolio , without it you are gambling)
- simple bits complex(every rule you add to a strategy is a clame that the future will resemble the past in one way or the other, a strategy with 3 rules makes 3 claim a strategy with 15 rules makes 15 claims , themore rule and parameter a strategy has the more the past can look great instead of being a machine until you meet reality)
- strategy that survive ages are just a hand full of rules, one clear why(a single economic reason to exist, robust works accrodss a wide range of values instead of just one magic setting )
- where does ideas actually come from?
    - Academic research(decade of academic research are out there with people measuring)
    - structure and mechanics(forced flows, rebalances,hedging,participants who must trade)
    - behavioral observation(you notice x after y, the different here is that the observation is the bagining of the work is not the end, instituotionals interogate it the idea arrives with a why attached to it.)

### **all of this anomalies the whys will most likely fall undo one of this strategies**

- Trend following(logic what has been moving in one direction tend to keep moving, low winrate big winners)
- mean reversion(what stetch to far will often snap back, high win rate , small winers)
- intra day bais, (pattern tiade to the clock, the day has a structure)
- swing(often a trend filter plus a pullback)
- Relative value(trade the gap btw two correlated assets direction agnostic)
- when your brainstorming around a trading strategy the first question is to whih family those that strategy belong to
- professonals dont necuessary run single versions of this strategy but multiple models wors together months after months
- Data(high quality data for the instrument)
    - your backtest cannot be better than the data you feed to it and bad data doesnt annouce it self(missing trades,bad ticks, settings confogirations)
    - before any test interrogate the data, does it cover enough markets, those the data comes from a reliable provider
    - Data to collect(Net profit(what history paid, tells you nothing about how you got there), winrate(read it only beside average profit and everage loss it is the balance), avararge trade(net profit over trades, must clear commisions and slippage), max drawdown(the worst stetch you would had had to sit though assume worse ahead), return on drawdown(what is the profit per unit of risk))
- In Code (the machine will replay every data in years, day by day, bar by bar)
- analyze(not just did it make money, How,When how painfully quesitoing if the profit is the result of an edge or just luck)
- Validate(the strategy tries to prove if what it has found is real)
    - **Monte Carlo simulation**(
        - Reshuffle(Reorder the same trades thousands of times, tight dispersion-means a good edge),
        - Bootstrap and resample (some trades repeat, others drop. the spaghetti chart with more insight)) this will generate thousands of equity curves all starting from thesame point and ending at thesame point here you can understand how much your strategy is sensitive to the edge siquence, you want a tiight distribution means your edge is stronger
        - the difference btw the reshuffle and bootstraping is that in the reshuffle we use thesame trade changing the order while in the bootstraping some of the trades might appear multiple times or not even appear
            - this what allow you to get more insights from the distribution you can get insights like what is the expectedprofit let say after 10 trades, what is the expected loss after 50 trades, what is the expected drowdown i should experience over a sample of thousands of  trades and this give you statistics to compare you live performance over statistics. and accept it as statistical event
            - what is the typical maximum drawdown
            - was it profitable and looking good just because of the oderng if the treade or there is a substantial edge?
            - how many paths ends in ruin
            - if you strategy only looks well in once equity curve and breaks in others means it was cause of luck and trade orders not a real edge
            - if it doesnt pass this test this strategy goes to the bin

### **Overfitting**

- overfitting is about adding conditions and rules making your strtegy extrimly complex yet fragile. extra filter to the strategy pr parameters each twick will learn about the past but less insight about the market behavior. the only way to understand if you overfitted is running an honest test that is applying your strategyto unseen data that is the split test
- you take all your data, you divide your data into in sample and out of sample
- you build and tune your parmeter only in sample
- once everything is ok you freeze your rule and apply to unseen data out of sample
- you will have a good edge if the result is good or similar in both
- a memorized pattern or am overfitted streaty will work only in the seen data

improvement iwth the position sizing

- working on postion sizing can be an effective way on improving performance without encountering overfitting risk
- for example we can set 1 contract of every single trade, meaning thatwith thesame size of 1 basedon the volatily of the instrument the solution is applying a volatily targetting an example is a specific amount of dollar per trade

when to say no

- we need to set the specific thresholds (what is the maximum strategy drowndown, what is the sepcifc profit , what is the specific menaing average trade profit that will make this straetegy vaiable )that a strategy must meet inorder to mvoe to the next step if arent satisfied this streatgy can go to the bin but dont see it as a lost see it as money saved, and if the results are there can be moved on.
- amateurs tries to be right, profesionals try to find out, if your research process doesnt say no its not an actual research process is a permission machine and the market will correct with your capital

Automation

- the strategy becomes code the code gets connected to the broker and the machine executes, we already have the sets of specific rules we backtested the same rules, there is no trade to sit infront of yor monitor and execute. it doesnt revent trade, doesnt question the strategy,doesnt trade with emotions

Monitoring

- while the maching is trading what do you do your job is no longer toexecute those trades manually but superviison, is the strategy that am seeing being execute thesame thing i backtested, you have your expected average trade win, you know what is the drawdown that you should expect, you know what is the expected rate to see that your strategy stays within the expected parameters, only this will tell you if it is working or its broken, it is this awarenemess of knowing what is expected that will keep the emotion
- when do you know the strategy isnt visible, when from the live exection the drawdown is above what the montel carlo from backtting simulation at that point you pause the structure becaue it isnt in the parameter anymore
- another option is slow degradation, you dont have a dramatic situation like experiencing drawdown but your average rate isnt getting anywere, that might be a sigh you need to pause or monitor that strategy, it can be that the edge you are taking advantage of isnt there anymore and that behavior isnt there anymore you dont wait for your equity curve to confirm that that is the reason you cant trade a single strategy but a set of encorelated strategy that runs at once

why you never trade just one strategy

- you might have periods were just one streategy rises and periods were nothing happens andthis doesnt garantee you will make money every month
- let say you add another strategy a mean reversion with a trend strategy when one of the strategy starts experiencing periods that a psychology brutaul th different models will remove those periods and increasing your chances of combining uncorrelated streties so that you dont rely on one single edge. so to conclude not one perfect working strategy that works well across every single mareket regime, and this is the sturcture that you must work towards

Infrastrcute vs process(while the instituining process doesnt transger the microsecnd speed, infomation infrastructure, isntrutional capital, the safty net the edge was always the process not the infrastructure) what actually transfers

- the why and the pipeline
- the monte carlo
- volatily based sizing automated execution