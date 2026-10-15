# Ideology-overlay — stage 1 measured report

## Result boundary

This MVP embeds 300 selected English passages (60 × 5 corpora) using the repository's existing Apple word-embedding path, then aligns corpus-local probe centroids. It does **not** test a language-independent human substrate: all vectors are already expressed by one English pretrained model. Results below are descriptive diagnostics only.

## Embedding coverage

- unique corpus/probe tokens: 2838 · Apple vectors found: 2394 · unavailable: 444
- passage vector: normalized mean of known word vectors; every passage retained at least one known token.
- anchors: for each of ten probes, mean of the five corpus passages nearest the probe. This construction favors apparent agreement and is therefore not confirmatory.

## Pairwise anchored alignment

Error = RMS coordinate error after orthogonal rotation of normalized anchor rows (lower is closer); mean cosine is reported alongside it. No null model, confidence interval, or held-out anchor test in this stage.

### left → right_trad

- anchor RMSE: **0.0043** · mean anchor cosine: **0.9972**

| probe | left representative | nearest right_trad after rotation | cosine |
|---|---|---|---:|
| the enemy | `left-007` All the Powers of old Europe have entered into a holy alliance to exorcise this spectre: Pope and Czar, Metternich and Guizot, French Radicals and Ge… | `right_trad-045` Those against whom it is not in my power to withhold the most grievous complaints are a part of that very soldiery which to this day have been so ful… | 0.984 |
| the hidden truth | `left-030` But Communism abolishes eternal truths, it abolishes all religion, and all morality, instead of constituting them on a new basis; it therefore acts i… | `right_trad-011` What are the religious, what the moral institutions they have taught among that people, as a guide to life, or as a consolation when life is to be no… | 0.981 |
| the children | `left-014` Do you charge us with wanting to stop the exploitation of children by their parents? | `right_trad-060` By this wise prejudice we are taught to look with horror on those children of their country who are prompt rashly to hack that aged parent in pieces … | 0.981 |
| the awakening | `left-009` Has it not preached in the place of these, charity and poverty, celibacy and mortification of the flesh, monastic life and Mother Church? | `right_trad-059` Through the same plan of a conformity to Nature in our artificial institutions, and by calling in the aid of her unerring and powerful instincts to f… | 0.983 |
| the fall | `left-005` In political practice, therefore, they join in all coercive measures against the working class; and in ordinary life, despite their high falutin phra… | `right_trad-009` In fine, by opening an avenue to the irruption of the Nabob of Arcot's creditors and soucars, whom every man, who did not fall in love with oppressio… | 0.986 |
| salvation | `left-009` Has it not preached in the place of these, charity and poverty, celibacy and mortification of the flesh, monastic life and Mother Church? | `right_trad-054` But "Fools rush in where angels fear to tread." In such a state of unbounded power, for undefined and undefinable purposes, the evil of a moral and a… | 0.981 |
| family | `left-004` The bourgeoisie has torn away from the family its sentimental veil, and has reduced the family relation to a mere money relation. | `right_trad-060` By this wise prejudice we are taught to look with horror on those children of their country who are prompt rashly to hack that aged parent in pieces … | 0.980 |
| betrayal | `left-010` Our bourgeois, not content with having the wives and daughters of their proletarians at their disposal, not to speak of common prostitutes, take the … | `right_trad-045` Those against whom it is not in my power to withhold the most grievous complaints are a part of that very soldiery which to this day have been so ful… | 0.983 |
| love | `left-050` In one word, you reproach us with intending to do away with your property. | `right_trad-049` That it was with a pain inexpressible he was obliged to have even the shadow of a difference with his friend, whose authority would always be great w… | 0.968 |
| fear | `left-014` Do you charge us with wanting to stop the exploitation of children by their parents? | `right_trad-047` Hope, fear, alarm, jealousy, the ephemerous tale that does its business and dies in a day, all these things, which are the reins and spurs by which l… | 0.981 |
### left → qanon

- anchor RMSE: **0.0062** · mean anchor cosine: **0.9942**

| probe | left representative | nearest qanon after rotation | cosine |
|---|---|---|---:|
| the enemy | `left-007` All the Powers of old Europe have entered into a holy alliance to exorcise this spectre: Pope and Czar, Metternich and Guizot, French Radicals and Ge… | `qanon-011` They are the true Patriots. We will never forget. Let these coming days be remembered in our history as the time we fought to recapture the republic … | 0.982 |
| the hidden truth | `left-030` But Communism abolishes eternal truths, it abolishes all religion, and all morality, instead of constituting them on a new basis; it therefore acts i… | `qanon-040` What happens when the public finds out the TRUTH? What happens when the FAKE NEWS MEDIA can no longer control the narrative (when disinformation is n… | 0.974 |
| the children | `left-014` Do you charge us with wanting to stop the exploitation of children by their parents? | `qanon-015` Angela Dorothea Kasner. Daughter of a Pastor? Name of FATHER? History of FATHER? Hitler youth (member). Haircut today vs THEN (A). Symbolic. US Intel… | 0.973 |
| the awakening | `left-009` Has it not preached in the place of these, charity and poverty, celibacy and mortification of the flesh, monastic life and Mother Church? | `qanon-040` What happens when the public finds out the TRUTH? What happens when the FAKE NEWS MEDIA can no longer control the narrative (when disinformation is n… | 0.965 |
| the fall | `left-005` In political practice, therefore, they join in all coercive measures against the working class; and in ordinary life, despite their high falutin phra… | `qanon-007` What data just dropped? Why is this relevant? HUMA. HUMA. HUMA. Where is HUMA? Who is HUMA connected to? What organization? What is HUMA's family his… | 0.977 |
| salvation | `left-009` Has it not preached in the place of these, charity and poverty, celibacy and mortification of the flesh, monastic life and Mother Church? | `qanon-037` Sometimes you can't TELL the public the truth. YOU MUST SHOW THEM. ONLY THEN WILL PEOPLE FIND THE WILL TO CHANGE. Crimes against children unite all h… | 0.978 |
| family | `left-004` The bourgeoisie has torn away from the family its sentimental veil, and has reduced the family relation to a mere money relation. | `qanon-015` Angela Dorothea Kasner. Daughter of a Pastor? Name of FATHER? History of FATHER? Hitler youth (member). Haircut today vs THEN (A). Symbolic. US Intel… | 0.974 |
| betrayal | `left-010` Our bourgeois, not content with having the wives and daughters of their proletarians at their disposal, not to speak of common prostitutes, take the … | `qanon-037` Sometimes you can't TELL the public the truth. YOU MUST SHOW THEM. ONLY THEN WILL PEOPLE FIND THE WILL TO CHANGE. Crimes against children unite all h… | 0.975 |
| love | `left-050` In one word, you reproach us with intending to do away with your property. | `qanon-051` They want one thing, and only one thing, POWER. They will LIE, CHEAT, and PROMISE YOU THE WORLD to obtain it. They do not love our Country. They desp… | 0.974 |
| fear | `left-014` Do you charge us with wanting to stop the exploitation of children by their parents? | `qanon-049` We stand w/ the good people of IRAN who are currently battling their 'installed' regime for FREEDOM. TRUE RULE, THE PEOPLE HAVE THE POWER. RISE UP an… | 0.971 |
### left → ufo

- anchor RMSE: **0.0053** · mean anchor cosine: **0.9957**

| probe | left representative | nearest ufo after rotation | cosine |
|---|---|---|---:|
| the enemy | `left-007` All the Powers of old Europe have entered into a holy alliance to exorcise this spectre: Pope and Czar, Metternich and Guizot, French Radicals and Ge… | `ufo-004` The invariable, or the real and stable, would be nothing at all in Intermediateness--rather as, but in relative terms, an undistorted interpretation … | 0.967 |
| the hidden truth | `left-030` But Communism abolishes eternal truths, it abolishes all religion, and all morality, instead of constituting them on a new basis; it therefore acts i… | `ufo-002` By positiveness we mean: Harmony, equilibrium, order, regularity, stability, consistency, unity, realness, system, government, organization, liberty,… | 0.974 |
| the children | `left-014` Do you charge us with wanting to stop the exploitation of children by their parents? | `ufo-016` Absolutely it was cast by an unknown body." According to our religion, if he had then given all his time to the maintaining of this one stand, of cou… | 0.977 |
| the awakening | `left-009` Has it not preached in the place of these, charity and poverty, celibacy and mortification of the flesh, monastic life and Mother Church? | `ufo-004` The invariable, or the real and stable, would be nothing at all in Intermediateness--rather as, but in relative terms, an undistorted interpretation … | 0.977 |
| the fall | `left-005` In political practice, therefore, they join in all coercive measures against the working class; and in ordinary life, despite their high falutin phra… | `ufo-025` If from a clear sky, or a sky in which there were no driven clouds, or other evidences of still-continuing wind-power--or, if from a storm in Florida… | 0.969 |
| salvation | `left-009` Has it not preached in the place of these, charity and poverty, celibacy and mortification of the flesh, monastic life and Mother Church? | `ufo-002` By positiveness we mean: Harmony, equilibrium, order, regularity, stability, consistency, unity, realness, system, government, organization, liberty,… | 0.978 |
| family | `left-004` The bourgeoisie has torn away from the family its sentimental veil, and has reduced the family relation to a mere money relation. | `ufo-016` Absolutely it was cast by an unknown body." According to our religion, if he had then given all his time to the maintaining of this one stand, of cou… | 0.980 |
| betrayal | `left-010` Our bourgeois, not content with having the wives and daughters of their proletarians at their disposal, not to speak of common prostitutes, take the … | `ufo-016` Absolutely it was cast by an unknown body." According to our religion, if he had then given all his time to the maintaining of this one stand, of cou… | 0.980 |
| love | `left-050` In one word, you reproach us with intending to do away with your property. | `ufo-008` Some day I shall tell the story of the _Marie Celeste_--"properly," as the _Scientific American Supplement_ would say--mysterious disappearance of a … | 0.943 |
| fear | `left-014` Do you charge us with wanting to stop the exploitation of children by their parents? | `ufo-004` The invariable, or the real and stable, would be nothing at all in Intermediateness--rather as, but in relative terms, an undistorted interpretation … | 0.979 |
### left → scripture

- anchor RMSE: **0.0051** · mean anchor cosine: **0.9961**

| probe | left representative | nearest scripture after rotation | cosine |
|---|---|---|---:|
| the enemy | `left-007` All the Powers of old Europe have entered into a holy alliance to exorcise this spectre: Pope and Czar, Metternich and Guizot, French Radicals and Ge… | `scripture-010` And Joseph wept when they spake unto him. 50:18 And his brethren also went and fell down before his face; and they said, Behold, we be thy servants. … | 0.979 |
| the hidden truth | `left-030` But Communism abolishes eternal truths, it abolishes all religion, and all morality, instead of constituting them on a new basis; it therefore acts i… | `scripture-045` Be of good cheer! [Hide, the holy Krishna saith, This from him that hath no faith, Him that worships not, nor seeks Wisdom's teaching when she speaks… | 0.972 |
| the children | `left-014` Do you charge us with wanting to stop the exploitation of children by their parents? | `scripture-025` And he had judged Israel forty years. 4:19 And his daughter in law, Phinehas’ wife, was with child, near to be delivered: and when she heard the tidi… | 0.978 |
| the awakening | `left-009` Has it not preached in the place of these, charity and poverty, celibacy and mortification of the flesh, monastic life and Mother Church? | `scripture-044` Who, unto friend and foe Keeping an equal heart, with equal mind Bears shame and glory; with an equal peace Takes heat and cold, pleasure and pain; a… | 0.968 |
| the fall | `left-005` In political practice, therefore, they join in all coercive measures against the working class; and in ordinary life, despite their high falutin phra… | `scripture-035` Ah! if in anger now Thou shouldst remember I did think Thee Friend, Speaking with easy speech, As men use each to each; Did call Thee "Krishna," "Pri… | 0.970 |
| salvation | `left-009` Has it not preached in the place of these, charity and poverty, celibacy and mortification of the flesh, monastic life and Mother Church? | `scripture-045` Be of good cheer! [Hide, the holy Krishna saith, This from him that hath no faith, Him that worships not, nor seeks Wisdom's teaching when she speaks… | 0.972 |
| family | `left-004` The bourgeoisie has torn away from the family its sentimental veil, and has reduced the family relation to a mere money relation. | `scripture-025` And he had judged Israel forty years. 4:19 And his daughter in law, Phinehas’ wife, was with child, near to be delivered: and when she heard the tidi… | 0.979 |
| betrayal | `left-010` Our bourgeois, not content with having the wives and daughters of their proletarians at their disposal, not to speak of common prostitutes, take the … | `scripture-044` Who, unto friend and foe Keeping an equal heart, with equal mind Bears shame and glory; with an equal peace Takes heat and cold, pleasure and pain; a… | 0.970 |
| love | `left-050` In one word, you reproach us with intending to do away with your property. | `scripture-010` And Joseph wept when they spake unto him. 50:18 And his brethren also went and fell down before his face; and they said, Behold, we be thy servants. … | 0.972 |
| fear | `left-014` Do you charge us with wanting to stop the exploitation of children by their parents? | `scripture-010` And Joseph wept when they spake unto him. 50:18 And his brethren also went and fell down before his face; and they said, Behold, we be thy servants. … | 0.979 |
### right_trad → qanon

- anchor RMSE: **0.0055** · mean anchor cosine: **0.9955**

| probe | right_trad representative | nearest qanon after rotation | cosine |
|---|---|---|---:|
| the enemy | `right_trad-024` He augments the power of his enemy by the very means he must take to contend with him. | `qanon-011` They are the true Patriots. We will never forget. Let these coming days be remembered in our history as the time we fought to recapture the republic … | 0.983 |
| the hidden truth | `right_trad-035` We have referred as well to those papers as to all the other proceedings on this subject, and must confess they fall very short of demonstrating to u… | `qanon-040` What happens when the public finds out the TRUTH? What happens when the FAKE NEWS MEDIA can no longer control the narrative (when disinformation is n… | 0.973 |
| the children | `right_trad-060` By this wise prejudice we are taught to look with horror on those children of their country who are prompt rashly to hack that aged parent in pieces … | `qanon-015` Angela Dorothea Kasner. Daughter of a Pastor? Name of FATHER? History of FATHER? Hitler youth (member). Haircut today vs THEN (A). Symbolic. US Intel… | 0.976 |
| the awakening | `right_trad-044` A man amongst them of great authority, and certainly of great talents, speaking of a supposed alliance between Church and State, says, "Perhaps _we m… | `qanon-022` https://twitter.com/Pismo_B/status/1223275776163794945 What happens when people learn the TRUTH? What happens when people WAKE UP? They will not be a… | 0.967 |
| the fall | `right_trad-005` It is not a predilection to mean, sordid, home-bred cares that will avert the consequences of a false estimation of our interest, or prevent the sham… | `qanon-025` THE SWAMP RUNS DEEP. Sometimes you cannot tell people the truth. You must show them. Only then, at the precipice, will people find the will to change… | 0.977 |
| salvation | `right_trad-006` Peters, concluding a long prayer at the royal chapel at Whitehall, (he had very triumphantly chosen his place,) said, "I have prayed and preached the… | `qanon-025` THE SWAMP RUNS DEEP. Sometimes you cannot tell people the truth. You must show them. Only then, at the precipice, will people find the will to change… | 0.981 |
| family | `right_trad-007` Fraud, injustice, oppression, peculation, engendered in India, are crimes of the same blood, family, and cast with those that are born and bred in En… | `qanon-015` Angela Dorothea Kasner. Daughter of a Pastor? Name of FATHER? History of FATHER? Hitler youth (member). Haircut today vs THEN (A). Symbolic. US Intel… | 0.980 |
| betrayal | `right_trad-005` It is not a predilection to mean, sordid, home-bred cares that will avert the consequences of a false estimation of our interest, or prevent the sham… | `qanon-037` Sometimes you can't TELL the public the truth. YOU MUST SHOW THEM. ONLY THEN WILL PEOPLE FIND THE WILL TO CHANGE. Crimes against children unite all h… | 0.972 |
| love | `right_trad-020` He ought to love and respect his kind, and to fear himself. | `qanon-051` They want one thing, and only one thing, POWER. They will LIE, CHEAT, and PROMISE YOU THE WORLD to obtain it. They do not love our Country. They desp… | 0.980 |
| fear | `right_trad-021` We tolerate even these,--not from love of them, but for fear of worse. | `qanon-055` https://twitter.com/An0n661/status/1258417972361732102 When do you expend ammunition? For what purpose? Prevent public exposure of truth [slow limit … | 0.968 |
### right_trad → ufo

- anchor RMSE: **0.0066** · mean anchor cosine: **0.9935**

| probe | right_trad representative | nearest ufo after rotation | cosine |
|---|---|---|---:|
| the enemy | `right_trad-024` He augments the power of his enemy by the very means he must take to contend with him. | `ufo-004` The invariable, or the real and stable, would be nothing at all in Intermediateness--rather as, but in relative terms, an undistorted interpretation … | 0.971 |
| the hidden truth | `right_trad-035` We have referred as well to those papers as to all the other proceedings on this subject, and must confess they fall very short of demonstrating to u… | `ufo-002` By positiveness we mean: Harmony, equilibrium, order, regularity, stability, consistency, unity, realness, system, government, organization, liberty,… | 0.977 |
| the children | `right_trad-060` By this wise prejudice we are taught to look with horror on those children of their country who are prompt rashly to hack that aged parent in pieces … | `ufo-016` Absolutely it was cast by an unknown body." According to our religion, if he had then given all his time to the maintaining of this one stand, of cou… | 0.977 |
| the awakening | `right_trad-044` A man amongst them of great authority, and certainly of great talents, speaking of a supposed alliance between Church and State, says, "Perhaps _we m… | `ufo-004` The invariable, or the real and stable, would be nothing at all in Intermediateness--rather as, but in relative terms, an undistorted interpretation … | 0.980 |
| the fall | `right_trad-005` It is not a predilection to mean, sordid, home-bred cares that will avert the consequences of a false estimation of our interest, or prevent the sham… | `ufo-004` The invariable, or the real and stable, would be nothing at all in Intermediateness--rather as, but in relative terms, an undistorted interpretation … | 0.974 |
| salvation | `right_trad-006` Peters, concluding a long prayer at the royal chapel at Whitehall, (he had very triumphantly chosen his place,) said, "I have prayed and preached the… | `ufo-004` The invariable, or the real and stable, would be nothing at all in Intermediateness--rather as, but in relative terms, an undistorted interpretation … | 0.977 |
| family | `right_trad-007` Fraud, injustice, oppression, peculation, engendered in India, are crimes of the same blood, family, and cast with those that are born and bred in En… | `ufo-016` Absolutely it was cast by an unknown body." According to our religion, if he had then given all his time to the maintaining of this one stand, of cou… | 0.980 |
| betrayal | `right_trad-005` It is not a predilection to mean, sordid, home-bred cares that will avert the consequences of a false estimation of our interest, or prevent the sham… | `ufo-016` Absolutely it was cast by an unknown body." According to our religion, if he had then given all his time to the maintaining of this one stand, of cou… | 0.975 |
| love | `right_trad-020` He ought to love and respect his kind, and to fear himself. | `ufo-016` Absolutely it was cast by an unknown body." According to our religion, if he had then given all his time to the maintaining of this one stand, of cou… | 0.954 |
| fear | `right_trad-021` We tolerate even these,--not from love of them, but for fear of worse. | `ufo-004` The invariable, or the real and stable, would be nothing at all in Intermediateness--rather as, but in relative terms, an undistorted interpretation … | 0.977 |
### right_trad → scripture

- anchor RMSE: **0.0053** · mean anchor cosine: **0.9958**

| probe | right_trad representative | nearest scripture after rotation | cosine |
|---|---|---|---:|
| the enemy | `right_trad-024` He augments the power of his enemy by the very means he must take to contend with him. | `scripture-010` And Joseph wept when they spake unto him. 50:18 And his brethren also went and fell down before his face; and they said, Behold, we be thy servants. … | 0.984 |
| the hidden truth | `right_trad-035` We have referred as well to those papers as to all the other proceedings on this subject, and must confess they fall very short of demonstrating to u… | `scripture-010` And Joseph wept when they spake unto him. 50:18 And his brethren also went and fell down before his face; and they said, Behold, we be thy servants. … | 0.975 |
| the children | `right_trad-060` By this wise prejudice we are taught to look with horror on those children of their country who are prompt rashly to hack that aged parent in pieces … | `scripture-025` And he had judged Israel forty years. 4:19 And his daughter in law, Phinehas’ wife, was with child, near to be delivered: and when she heard the tidi… | 0.979 |
| the awakening | `right_trad-044` A man amongst them of great authority, and certainly of great talents, speaking of a supposed alliance between Church and State, says, "Perhaps _we m… | `scripture-045` Be of good cheer! [Hide, the holy Krishna saith, This from him that hath no faith, Him that worships not, nor seeks Wisdom's teaching when she speaks… | 0.970 |
| the fall | `right_trad-005` It is not a predilection to mean, sordid, home-bred cares that will avert the consequences of a false estimation of our interest, or prevent the sham… | `scripture-010` And Joseph wept when they spake unto him. 50:18 And his brethren also went and fell down before his face; and they said, Behold, we be thy servants. … | 0.971 |
| salvation | `right_trad-006` Peters, concluding a long prayer at the royal chapel at Whitehall, (he had very triumphantly chosen his place,) said, "I have prayed and preached the… | `scripture-045` Be of good cheer! [Hide, the holy Krishna saith, This from him that hath no faith, Him that worships not, nor seeks Wisdom's teaching when she speaks… | 0.979 |
| family | `right_trad-007` Fraud, injustice, oppression, peculation, engendered in India, are crimes of the same blood, family, and cast with those that are born and bred in En… | `scripture-025` And he had judged Israel forty years. 4:19 And his daughter in law, Phinehas’ wife, was with child, near to be delivered: and when she heard the tidi… | 0.982 |
| betrayal | `right_trad-005` It is not a predilection to mean, sordid, home-bred cares that will avert the consequences of a false estimation of our interest, or prevent the sham… | `scripture-044` Who, unto friend and foe Keeping an equal heart, with equal mind Bears shame and glory; with an equal peace Takes heat and cold, pleasure and pain; a… | 0.970 |
| love | `right_trad-020` He ought to love and respect his kind, and to fear himself. | `scripture-010` And Joseph wept when they spake unto him. 50:18 And his brethren also went and fell down before his face; and they said, Behold, we be thy servants. … | 0.979 |
| fear | `right_trad-021` We tolerate even these,--not from love of them, but for fear of worse. | `scripture-010` And Joseph wept when they spake unto him. 50:18 And his brethren also went and fell down before his face; and they said, Behold, we be thy servants. … | 0.972 |
### qanon → ufo

- anchor RMSE: **0.0071** · mean anchor cosine: **0.9925**

| probe | qanon representative | nearest ufo after rotation | cosine |
|---|---|---|---:|
| the enemy | `qanon-042` Patriot - A little perspective… Patriots are dying to defend this great country and the FREEDOM she provides. Children are being kidnapped, tortured,… | `ufo-060` Extraordinary--we fear he must have been a man of loose habits in some other respects. | 0.967 |
| the hidden truth | `qanon-057` https://www.youtube.com/watch?v=6NedgyDfZpY Truth to Power. Listen carefully. Q | `ufo-002` By positiveness we mean: Harmony, equilibrium, order, regularity, stability, consistency, unity, realness, system, government, organization, liberty,… | 0.977 |
| the children | `qanon-015` Angela Dorothea Kasner. Daughter of a Pastor? Name of FATHER? History of FATHER? Hitler youth (member). Haircut today vs THEN (A). Symbolic. US Intel… | `ufo-016` Absolutely it was cast by an unknown body." According to our religion, if he had then given all his time to the maintaining of this one stand, of cou… | 0.975 |
| the awakening | `qanon-059` https://www.youtube.com/watch?v=QR1NnBA4HMI&feature=youtu.be The Great Awakening. Q | `ufo-022` Though in some respects our own Intermediatism is unsatisfactory, our underlying feeling is-- That in a dreaming mind awakening is accelerated--if ph… | 0.964 |
| the fall | `qanon-036` We are being set up. Threat. Past Booms - TX bombs New Booms - Plane crash + Plane/17 drop. These people are sick. Attempt to prevent drops / awakeni… | `ufo-004` The invariable, or the real and stable, would be nothing at all in Intermediateness--rather as, but in relative terms, an undistorted interpretation … | 0.970 |
| salvation | `qanon-009` Patriot, your country needs you. You are not alone. God is LOVE. 2018 will be GLORIOUS! God bless, Q | `ufo-016` Absolutely it was cast by an unknown body." According to our religion, if he had then given all his time to the maintaining of this one stand, of cou… | 0.968 |
| family | `qanon-015` Angela Dorothea Kasner. Daughter of a Pastor? Name of FATHER? History of FATHER? Hitler youth (member). Haircut today vs THEN (A). Symbolic. US Intel… | `ufo-016` Absolutely it was cast by an unknown body." According to our religion, if he had then given all his time to the maintaining of this one stand, of cou… | 0.980 |
| betrayal | `qanon-037` Sometimes you can't TELL the public the truth. YOU MUST SHOW THEM. ONLY THEN WILL PEOPLE FIND THE WILL TO CHANGE. Crimes against children unite all h… | `ufo-016` Absolutely it was cast by an unknown body." According to our religion, if he had then given all his time to the maintaining of this one stand, of cou… | 0.975 |
| love | `qanon-009` Patriot, your country needs you. You are not alone. God is LOVE. 2018 will be GLORIOUS! God bless, Q | `ufo-009` Lescarbault wrote to Leverrier, who hastened to Orgeres-- Because this announcement assimilated with his own calculations upon a planet between Mercu… | 0.953 |
| fear | `qanon-032` https://twitter.com/TrueQanuck11/status/1210948219494162432 PANIC mode. People awake is their greatest fear. Q | `ufo-004` The invariable, or the real and stable, would be nothing at all in Intermediateness--rather as, but in relative terms, an undistorted interpretation … | 0.974 |
### qanon → scripture

- anchor RMSE: **0.0061** · mean anchor cosine: **0.9945**

| probe | qanon representative | nearest scripture after rotation | cosine |
|---|---|---|---:|
| the enemy | `qanon-042` Patriot - A little perspective… Patriots are dying to defend this great country and the FREEDOM she provides. Children are being kidnapped, tortured,… | `scripture-010` And Joseph wept when they spake unto him. 50:18 And his brethren also went and fell down before his face; and they said, Behold, we be thy servants. … | 0.977 |
| the hidden truth | `qanon-057` https://www.youtube.com/watch?v=6NedgyDfZpY Truth to Power. Listen carefully. Q | `scripture-059` Moreover, when a soul departeth, fixed In Soothfastness, it goeth to the place-- Perfect and pure--of those that know all Truth. | 0.969 |
| the children | `qanon-015` Angela Dorothea Kasner. Daughter of a Pastor? Name of FATHER? History of FATHER? Hitler youth (member). Haircut today vs THEN (A). Symbolic. US Intel… | `scripture-025` And he had judged Israel forty years. 4:19 And his daughter in law, Phinehas’ wife, was with child, near to be delivered: and when she heard the tidi… | 0.976 |
| the awakening | `qanon-059` https://www.youtube.com/watch?v=QR1NnBA4HMI&feature=youtu.be The Great Awakening. Q | `scripture-044` Who, unto friend and foe Keeping an equal heart, with equal mind Bears shame and glory; with an equal peace Takes heat and cold, pleasure and pain; a… | 0.959 |
| the fall | `qanon-036` We are being set up. Threat. Past Booms - TX bombs New Booms - Plane crash + Plane/17 drop. These people are sick. Attempt to prevent drops / awakeni… | `scripture-035` Ah! if in anger now Thou shouldst remember I did think Thee Friend, Speaking with easy speech, As men use each to each; Did call Thee "Krishna," "Pri… | 0.968 |
| salvation | `qanon-009` Patriot, your country needs you. You are not alone. God is LOVE. 2018 will be GLORIOUS! God bless, Q | `scripture-010` And Joseph wept when they spake unto him. 50:18 And his brethren also went and fell down before his face; and they said, Behold, we be thy servants. … | 0.980 |
| family | `qanon-015` Angela Dorothea Kasner. Daughter of a Pastor? Name of FATHER? History of FATHER? Hitler youth (member). Haircut today vs THEN (A). Symbolic. US Intel… | `scripture-025` And he had judged Israel forty years. 4:19 And his daughter in law, Phinehas’ wife, was with child, near to be delivered: and when she heard the tidi… | 0.984 |
| betrayal | `qanon-037` Sometimes you can't TELL the public the truth. YOU MUST SHOW THEM. ONLY THEN WILL PEOPLE FIND THE WILL TO CHANGE. Crimes against children unite all h… | `scripture-044` Who, unto friend and foe Keeping an equal heart, with equal mind Bears shame and glory; with an equal peace Takes heat and cold, pleasure and pain; a… | 0.963 |
| love | `qanon-009` Patriot, your country needs you. You are not alone. God is LOVE. 2018 will be GLORIOUS! God bless, Q | `scripture-010` And Joseph wept when they spake unto him. 50:18 And his brethren also went and fell down before his face; and they said, Behold, we be thy servants. … | 0.975 |
| fear | `qanon-032` https://twitter.com/TrueQanuck11/status/1210948219494162432 PANIC mode. People awake is their greatest fear. Q | `scripture-033` And there be evil doers; loose of heart, Low-minded, stubborn, fraudulent, remiss, Dull, slow, despondent--children of the "dark." Hear, too, of Inte… | 0.968 |
### ufo → scripture

- anchor RMSE: **0.0056** · mean anchor cosine: **0.9954**

| probe | ufo representative | nearest scripture after rotation | cosine |
|---|---|---|---:|
| the enemy | `ufo-001` Though everyone who scalps is, in the oneness of allness, himself likely to be scalped, there is such a discourtesy to an enemy as the wearing of wig… | `scripture-010` And Joseph wept when they spake unto him. 50:18 And his brethren also went and fell down before his face; and they said, Behold, we be thy servants. … | 0.979 |
| the hidden truth | `ufo-005` In our acceptance, logic, science, art, religion are, in our "existence," premonitions of a coming awakening, like dawning awarenesses of surrounding… | `scripture-045` Be of good cheer! [Hide, the holy Krishna saith, This from him that hath no faith, Him that worships not, nor seeks Wisdom's teaching when she speaks… | 0.965 |
| the children | `ufo-041` He had told his little son, aged five years, to look through the telescope. | `scripture-025` And he had judged Israel forty years. 4:19 And his daughter in law, Phinehas’ wife, was with child, near to be delivered: and when she heard the tidi… | 0.974 |
| the awakening | `ufo-019` In our acceptance, it is, in quasi-existence, premonitory, or pre-natal, or pre-awakening consciousness of a real existence. | `scripture-044` Who, unto friend and foe Keeping an equal heart, with equal mind Bears shame and glory; with an equal peace Takes heat and cold, pleasure and pain; a… | 0.967 |
| the fall | `ufo-028` As to other falls, or another fall, it is said in the _Amer. | `scripture-034` By Me they fall--not thee! the stroke of death is dealt them now, Even as they show thus gallantly; My instrument art thou! | 0.962 |
| salvation | `ufo-005` In our acceptance, logic, science, art, religion are, in our "existence," premonitions of a coming awakening, like dawning awarenesses of surrounding… | `scripture-045` Be of good cheer! [Hide, the holy Krishna saith, This from him that hath no faith, Him that worships not, nor seeks Wisdom's teaching when she speaks… | 0.975 |
| family | `ufo-018` Symons knew his writing desk-- Then comes the instance of a man, his wife, and his three daughters, at Casterton, Westmoreland, who were looking out … | `scripture-025` And he had judged Israel forty years. 4:19 And his daughter in law, Phinehas’ wife, was with child, near to be delivered: and when she heard the tidi… | 0.983 |
| betrayal | `ufo-010` In this oneness of allness, or continuity, the protecting hand strangles; the parental stifles; love is inseparable from phenomena of hate. | `scripture-044` Who, unto friend and foe Keeping an equal heart, with equal mind Bears shame and glory; with an equal peace Takes heat and cold, pleasure and pain; a… | 0.969 |
| love | `ufo-010` In this oneness of allness, or continuity, the protecting hand strangles; the parental stifles; love is inseparable from phenomena of hate. | `scripture-010` And Joseph wept when they spake unto him. 50:18 And his brethren also went and fell down before his face; and they said, Behold, we be thy servants. … | 0.985 |
| fear | `ufo-060` Extraordinary--we fear he must have been a man of loose habits in some other respects. | `scripture-010` And Joseph wept when they spake unto him. 50:18 And his brethren also went and fell down before his face; and they said, Behold, we be thy servants. … | 0.979 |

## Base-persona probe results

Top corpus passage by direct cosine to each persona word; these are lexical-model retrievals, not validated archetypes.

### left

| persona probe | top passage | cosine |
|---|---|---:|
| parent | `left-014` Do you charge us with wanting to stop the exploitation of children by their parents? | 1.641 |
| lover | `left-010` Our bourgeois, not content with having the wives and daughters of their proletarians at their disposal, not to speak of common prostitutes, take the … | 1.311 |
| child | `left-014` Do you charge us with wanting to stop the exploitation of children by their parents? | 1.694 |
| sibling | `left-014` Do you charge us with wanting to stop the exploitation of children by their parents? | 1.523 |
| friend | `left-050` In one word, you reproach us with intending to do away with your property. | 1.360 |
### right_trad

| persona probe | top passage | cosine |
|---|---|---:|
| parent | `right_trad-060` By this wise prejudice we are taught to look with horror on those children of their country who are prompt rashly to hack that aged parent in pieces … | 1.496 |
| lover | `right_trad-037` To such a length have his passions and violences carried him, that all my family, my dependants, and even my friends and visitors, are persecuted wit… | 1.324 |
| child | `right_trad-060` By this wise prejudice we are taught to look with horror on those children of their country who are prompt rashly to hack that aged parent in pieces … | 1.499 |
| sibling | `right_trad-060` By this wise prejudice we are taught to look with horror on those children of their country who are prompt rashly to hack that aged parent in pieces … | 1.495 |
| friend | `right_trad-037` To such a length have his passions and violences carried him, that all my family, my dependants, and even my friends and visitors, are persecuted wit… | 1.363 |
### qanon

| persona probe | top passage | cosine |
|---|---|---:|
| parent | `qanon-015` Angela Dorothea Kasner. Daughter of a Pastor? Name of FATHER? History of FATHER? Hitler youth (member). Haircut today vs THEN (A). Symbolic. US Intel… | 1.538 |
| lover | `qanon-009` Patriot, your country needs you. You are not alone. God is LOVE. 2018 will be GLORIOUS! God bless, Q | 1.330 |
| child | `qanon-015` Angela Dorothea Kasner. Daughter of a Pastor? Name of FATHER? History of FATHER? Hitler youth (member). Haircut today vs THEN (A). Symbolic. US Intel… | 1.499 |
| sibling | `qanon-018` https://www.dailymail.co.uk/news/article-6823155/Alan-Krueger-noted-economist-served-Obama-died.html "It is with tremendous sadness we share that Pro… | 1.566 |
| friend | `qanon-044` https://twitter.com/drewanon17/status/1262060653268791296 “We do not "get over" a death. We learn to carry the grief and integrate the loss in our li… | 1.397 |
### ufo

| persona probe | top passage | cosine |
|---|---|---:|
| parent | `ufo-041` He had told his little son, aged five years, to look through the telescope. | 1.418 |
| lover | `ufo-011` I fear me that the horse and the barn were a little extreme for our budding liberalities. | 1.243 |
| child | `ufo-041` He had told his little son, aged five years, to look through the telescope. | 1.454 |
| sibling | `ufo-041` He had told his little son, aged five years, to look through the telescope. | 1.547 |
| friend | `ufo-041` He had told his little son, aged five years, to look through the telescope. | 1.317 |
### scripture

| persona probe | top passage | cosine |
|---|---|---:|
| parent | `scripture-019` And she had compassion on him, and said, This is one of the Hebrews’ children. 2:7 Then said his sister to Pharaoh’s daughter, Shall I go and call to… | 1.520 |
| lover | `scripture-040` As father to a son, As friend to friend, as one Who loveth to his lover, turn Thy face In gentleness on me! | 1.513 |
| child | `scripture-019` And she had compassion on him, and said, This is one of the Hebrews’ children. 2:7 Then said his sister to Pharaoh’s daughter, Shall I go and call to… | 1.619 |
| sibling | `scripture-020` And all the people shall say, Amen. 27:22 Cursed be he that lieth with his sister, the daughter of his father, or the daughter of his mother. | 1.692 |
| friend | `scripture-040` As father to a son, As friend to friend, as one Who loveth to his lover, turn Thy face In gentleness on me! | 1.529 |

## Residual candidates

For each corpus passage, the score is its best cosine match in every other corpus after that pair's fitted rotation; lowest five are candidates for non-overlap. This is not a claim that a passage is uniquely ideological: selection, mean pooling, and a small corpus can all cause low matches.

### left

| candidate residual | best cross-corpus cosine |
|---|---:|
| `left-057` But if selling and buying disappears, free selling and buying disappears also. | 0.808 |
| `left-020` The abolition of bourgeois individuality, bourgeois independence, and bourgeois freedom is undoubtedly aimed at. | 0.824 |
| `left-056` We may cite Proudhon’s _Philosophie de la Misère_ as an example of this form. | 0.851 |
| `left-053` This form of Socialism has, moreover, been worked out into complete systems. | 0.876 |
| `left-054` It has agglomerated production, and has concentrated property in a few hands. | 0.878 |
### right_trad

| candidate residual | best cross-corpus cosine |
|---|---:|
| `right_trad-020` He ought to love and respect his kind, and to fear himself. | 0.910 |
| `right_trad-025` He never sought to be loved without putting himself first in a condition to be feared. | 0.911 |
| `right_trad-022` If the people are happy, united, wealthy, and powerful, we presume the rest. | 0.914 |
| `right_trad-010` Such a prodigy would have filled any common man with superstitious fears. | 0.915 |
| `right_trad-030` All other people have laid the foundations of civil freedom in severer manners, and a system of a more austere and masculine morality. | 0.916 |
### qanon

| candidate residual | best cross-corpus cosine |
|---|---:|
| `qanon-034` 7/10. Targeted Kills. Power Out. Flight re-routes. Flight returns. Running. Public awakening. Message spreading wide & far. Goodbye @Jack. Q | 0.837 |
| `qanon-059` https://www.youtube.com/watch?v=QR1NnBA4HMI&feature=youtu.be The Great Awakening. Q | 0.865 |
| `qanon-057` https://www.youtube.com/watch?v=6NedgyDfZpY Truth to Power. Listen carefully. Q | 0.866 |
| `qanon-032` https://twitter.com/TrueQanuck11/status/1210948219494162432 PANIC mode. People awake is their greatest fear. Q | 0.879 |
| `qanon-016` https://motherboard.vice.com/en_us/article/gy7mnx/google-ceo-says-no-plans-to-launch-dragonfly-chinese-search-engine-sundar-pichai Google CEO Says No Plan to ‘Launch’ Censored Search Engine in China" How do yo… | 0.890 |
### ufo

| candidate residual | best cross-corpus cosine |
|---|---:|
| `ufo-054` Falls of sandstone and limestone are repulsive to both theologians and scientists. | 0.819 |
| `ufo-046` Fall of great numbers of larvae of beetles, near Mortagne, France, May, 1858. | 0.829 |
| `ufo-048` I have data of other falls, in Persia and Asiatic Turkey, of edible substances. | 0.854 |
| `ufo-031` But concomitants of this fall: Loud noises were heard in the sky. | 0.871 |
| `ufo-036` Over and over have we noted the occurrence of strange falls in storms. | 0.884 |
### scripture

| candidate residual | best cross-corpus cosine |
|---|---:|
| `scripture-049` The very truth--Heart's Lord!--of Sannyas, Abstention; and enunciation, Lord! | 0.823 |
| `scripture-037` I will to thee unfold Some portions of My Majesty, whose powers are manifold! | 0.866 |
| `scripture-047` Yea! for its leaves Are green and waving hymns which whisper Truth! | 0.873 |
| `scripture-013` He said, Yea. 22:28 And the chief captain answered, With a great sum obtained I this freedom. | 0.877 |
| `scripture-053` This friendly human frame, my mind can think Calm thoughts once more; my heart beats still again! | 0.880 |

## What this stage does and does not find

- **No supported common skeleton claim.** High post-fit anchor similarity is expected partly because anchors were selected using the same English embedding and then fit on those same ten probes; there is no held-out validation.
- **Weak descriptive signal only:** all corpora yield retrievable passages near fear/love/family/persona words, but the retrieved text varies strongly with source wording and selector bias.
- **Residual lists are lexical candidates, not unique claims.** They require human coding and out-of-sample comparison before interpretation.

## Limits → next stage

1. 60 passages/corpus; sources are narrow, English translations/transcriptions, and themed selection is non-random.
2. Mean word vectors discard syntax, negation, speaker, historical context, and factual status.
3. Probe-derived anchors and fitted-pair concordance reuse the same data: circular for inference.
4. Q archive records unsupported/conspiratorial material; proximity never validates a claim.
5. Next: preregister a larger stratified corpus, independent human concept annotations, train/fit on one anchor split and evaluate held-out probes/passages against shuffled-corpus nulls; compare a contextual embedding model only if a repository-approved path is added.


## Artifacts

- `embeddings/*.jsonl` — per-passage vectors and token coverage
- `results/stage1-metrics.json` — full precision values and tables
- `SOURCES.md` — provenance and reproduction

