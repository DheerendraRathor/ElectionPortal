Election Documentation
======================

This documentation is for election creators. It contains guidelines to create and run elections.

Create Election
---------------

1. Visit [Election page]({% url 'admin:election_election_changelist' %}).
2. Click on link [Add Election]({% url 'admin:election_election_add' %})
3. Type name of election. Add posts (You can add posts later also).
4. Click on `Save and Continue Editing` Button

Check the button `Preview Page` to see election portal from the voters perspective.

### Election Options
#### Basic Options
- `Is active`: Check it to start election. Once started, it can't be unchecked. 
- `Is temporary closed`: This checkbox will get activated once election has been started. Check it to temporarily close
election. _This does not mean that election is finished._ It can be checked and unchecked multiple times.
- `Is finished`: Check it to finish an election. Election once finished can't be restarted again. You need to contact 
super admin to start election again!

Once you check `Is finished` you will be able to see `Get Results` button right next to `Preview Page` button.

#### Advanced Options
- `Is Key Required`: By default it is checked. If it is checked then voters will require a special pass key to vote. 
This passkey is generated automatically and can be downloaded from voters page.
- `Keep nota option`: If number of candidates are > 1 then there will be an option `None of these` will be available to
voters. `None of these` vote will be counted as negative vote for all candidates.
- `Display manifesto`: Display manifesto of candidates below their name. You need to upload manifesto for candidates 
during creation of candidates. 
- `Session Timeout`: Number of seconds before voter will be logged out automatically. This is kept to ensure voter will 
be logged out automatically on public machines. Voter can again login to vote.
- `Votes per IP`: Number of votes allowed per IP. If it is 0 then unlimited votes are allowed per IP. 


Create Posts
------------
Posts can be added from either election page or from [post page]({% url 'admin:post_post_add' %}). In second option you 
can add candidates as well. Once a election is started, no new candidates and posts can be added.

### Posts Options
- `Name`: Name of post
- `Number`: Number of available seats
- `Election`: Election of the post (This option will be available only when you're creating post from second method)
- `Type`: Choose one from `ALL`, `UG`, `PG`. In case of `UG` and `PG` only UG and PG voters will be allowed to vote 
respectively.
- `Order`: Order of display of post on election page. Smallest order value post will appear first.


Create Candidates
-----------------

Candidates can be added from post page. They have similar options as post and have additional options of creating image.


Adding Voters
-------------

Voters can be added in bulk or one by one. To add voters in bulk go to election page and click on the `Add voters`
button. You need to upload a CSV file containing list of voters. 

### Options
- `Roll Number Column`: Which column in your CSV list contains list of roll numbers. Remeber counting starts with 0.
- `Tags`: You can tag your voters in CSV list with upto five tags. Tags are useful for easy filtering of voters. 


You can also visit [Voters Page]({% url 'admin:election_voter_changelist' %}) to add/delete voters. Here you can filter your
voters by election and tags. You can't modify/delete a voter once election has been started. You still can add more
voters.


General Tips
============
- Voters are bound to election and not to posts. If your post has targeted voters like PG or UG voters then define 
your posts accordingly. 
- If your posts have no existing partition (like UG or PG) and you don't want to allow all registered voters to vote for
that post then consider creating another election with that post and limited number of voters.  
For e.g. Your department are having elections and there are posts like "General Secretary", "Class Representative 2016",
 "Class Representative 2017" etc. Here you want all voters to vote for GS post but want only certain voters to vote for 
 "CR 2016" post. In this scenario you should create 3 elections. Add voters to corresponding elections and while voting 
 voters will first vote for GS election and then "CR 2016" election. This portal is designed to handle multiple 
 elections if one voter is eligible to vote in multiple elections.