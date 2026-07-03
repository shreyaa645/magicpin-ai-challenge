from app.storage import contexts


def process_tick(trigger_ids):
    actions = []
    trigger_store = contexts.get("trigger", {})
    merchant_store = contexts.get("merchant", {})

    for tid in trigger_ids:
        trigger = trigger_store.get(tid)
        if not trigger:
            continue

        merchant_id = trigger.get("merchant_id")
        merchant = merchant_store.get(merchant_id)
        if not merchant:
            continue

        body = compose_message(trigger, merchant)
        if not body:
            continue

        actions.append(
            {
                "trigger_id": tid,
                "merchant_id": merchant_id,
                "customer_id": trigger.get("customer_id"),
                "body": body,
                "cta": "Reply YES",
                "send_as": "vera",
                "suppression_key": trigger.get("suppression_key")
            }
        )

    return actions


def compose_message(trigger, merchant):
    identity = merchant.get("identity", {}) or {}
    merchant_name = identity.get("name") or identity.get("owner_first_name") or "Merchant"
    city = identity.get("city")
    locality = identity.get("locality")
    category = (merchant.get("category_slug") or "").lower()
    subscription = merchant.get("subscription", {}) or {}
    performance = merchant.get("performance", {}) or {}
    signals = merchant.get("signals", []) or []
    offers = merchant.get("offers", []) or []
    review_themes = merchant.get("review_themes", []) or []

    location = ", ".join([part for part in [locality, city] if part])
    greeting = f"Hi {merchant_name}" + (f" — {location}" if location else "")

    intro = greeting + "."
    kind = trigger.get("kind", "")
    payload = trigger.get("payload", {}) or {}

    body = None

    if kind == "research_digest":
        body = research_digest_message(intro, category, performance, signals, offers)
    elif kind == "regulation_change":
        body = regulation_change_message(intro, category, payload)
    elif kind == "recall_due":
        body = recall_due_message(intro, category, payload)
    elif kind == "perf_dip":
        body = perf_dip_message(intro, category, payload, performance, offers)
    elif kind == "renewal_due":
        body = renewal_due_message(intro, category, payload, subscription)
    elif kind == "festival_upcoming":
        body = festival_upcoming_message(intro, category, payload, offers)
    elif kind == "wedding_package_followup":
        body = wedding_package_followup_message(intro, category, payload)
    elif kind == "curious_ask_due":
        body = curious_ask_due_message(intro, category, payload)
    elif kind == "winback_eligible":
        body = winback_eligible_message(intro, category, payload)
    elif kind == "ipl_match_today":
        body = ipl_match_today_message(intro, category, payload)
    elif kind == "review_theme_emerged":
        body = review_theme_emerged_message(intro, category, payload)
    elif kind == "milestone_reached":
        body = milestone_reached_message(intro, category, payload)
    elif kind == "active_planning_intent":
        body = active_planning_intent_message(intro, category, payload)
    elif kind == "seasonal_perf_dip":
        body = seasonal_perf_dip_message(intro, category, payload, performance)
    elif kind == "customer_lapsed_hard":
        body = customer_lapsed_hard_message(intro, category, payload)
    elif kind == "trial_followup":
        body = trial_followup_message(intro, category, payload)
    elif kind == "supply_alert":
        body = supply_alert_message(intro, category, payload)
    elif kind == "chronic_refill_due":
        body = chronic_refill_due_message(intro, category, payload)
    elif kind == "category_seasonal":
        body = category_seasonal_message(intro, category, payload)
    elif kind == "gbp_unverified":
        body = gbp_unverified_message(intro, category, payload)
    elif kind == "cde_opportunity":
        body = cde_opportunity_message(intro, category, payload)
    elif kind == "competitor_opened":
        body = competitor_opened_message(intro, category, payload)
    elif kind == "perf_spike":
        body = perf_spike_message(intro, category, payload, performance)
    elif kind == "dormant_with_vera":
        body = dormant_with_vera_message(intro, category, payload)
    else:
        body = fallback_message(intro, category, performance, signals, offers)

    return body


def research_digest_message(intro, category, performance, signals, offers):
    highlight = ""
    if "ctr_below_peer_median" in signals:
        highlight = "Your CTR is still below peer median."
    elif performance.get("ctr") is not None:
        highlight = f"Your current CTR is {format_pct(performance.get('ctr'), absolute=True)}."

    offer_line = ""
    active_offer = first_active_offer(offers)
    if active_offer:
        offer_line = f"Your active offer {active_offer} is a strong starting point."

    action = (
        "I can turn this research into a short Google Business Profile post or patient follow-up note. "
        "Would you like me to draft that?"
    )

    return join_paragraphs(intro, "New category research is available for your business.", highlight, offer_line, action)


def regulation_change_message(intro, category, payload):
    deadline = payload.get("deadline_iso") or payload.get("deadline")
    topic = safe_keyword(payload.get("top_item_id")) or safe_keyword(payload.get("topic")) or category
    topic_line = f"There is a new {topic.replace('_', ' ')} requirement for your category." if topic else "There is a new compliance update for your category."
    deadline_line = f"The deadline is {deadline}." if deadline else "The deadline is approaching."
    recommendation = (
        "Let's make sure your profile and customer communication reflect this change before it becomes mandatory. "
        "Should I help you prepare the next step?"
    )

    return join_paragraphs(intro, topic_line, deadline_line, recommendation)


def recall_due_message(intro, category, payload):
    service_due = humanize_service(payload.get("service_due"))
    due_date = payload.get("due_date")
    slots = payload.get("available_slots", []) or []
    slot_text = first_slot_label(slots)

    service_line = f"A patient is due for {service_due}." if service_due else "A patient is due for a follow-up service."
    due_line = f"The next due date is {due_date}." if due_date else "The recall window is open now."
    slot_line = f"I can reach out with this slot: {slot_text}." if slot_text else "I can reach out with a few good appointment options."
    action = "Want me to prepare the message for the patient?"

    return join_paragraphs(intro, service_line, due_line, slot_line, action)


def perf_dip_message(intro, category, payload, performance, offers):
    metric = payload.get("metric") or "activity"
    delta_pct = format_pct(payload.get("delta_pct"))
    window = payload.get("window")
    baseline = payload.get("vs_baseline")
    metric_line = f"Your {metric} has dropped {delta_pct} over the last {window}." if delta_pct and window else f"Your {metric} trend is weaker than before."
    baseline_line = f"That is below the usual {baseline}." if baseline is not None else "This is a signal to act quickly."
    offer_line = f"A quick refresh of your offer or GBP post could help recover momentum." if first_active_offer(offers) else "A new offer or promotion can help bring attention back."
    action = "Should I draft a recovery message for you?"

    return join_paragraphs(intro, metric_line, baseline_line, offer_line, action)


def renewal_due_message(intro, category, payload, subscription):
    days = payload.get("days_remaining") if payload.get("days_remaining") is not None else subscription.get("days_remaining")
    plan = payload.get("plan") or subscription.get("plan")
    status = subscription.get("status")
    days_line = f"Your {plan or 'current'} plan renews in {int(days)} days." if days is not None else "Your renewal is coming up soon."
    status_line = "We should avoid any service interruption." if status == "active" else "Let's reinstate your services without delay." if status == "expired" else ""
    action = "Can I help you complete the renewal now?"

    return join_paragraphs(intro, days_line, status_line, action)


def festival_upcoming_message(intro, category, payload, offers):
    festival = payload.get("festival") or "the upcoming festival"
    days = payload.get("days_until")
    when = f"in {int(days)} days" if days is not None else "soon"
    idea = category_festival_suggestion(category, festival)
    action = "Would you like me to build that campaign for you?"

    return join_paragraphs(intro, f"{festival} is {when}.", idea, action)


def wedding_package_followup_message(intro, category, payload):
    days = payload.get("days_to_wedding")
    next_step = payload.get("next_step_window_open")
    wedding_line = f"A bridal customer is still in the planning window, with {int(days)} days until the wedding." if days is not None else "A wedding package customer is in the follow-up phase."
    step_line = f"The next step is {next_step.replace('_', ' ')}." if next_step else "The next service step is open now."
    action = "Should I draft the follow-up message?"

    return join_paragraphs(intro, wedding_line, step_line, action)


def curious_ask_due_message(intro, category, payload):
    ask = payload.get("ask_template") or "a customer curiosity check"
    ask_line = f"It's time for your next market check: {ask.replace('_', ' ')}."
    idea = "A short question to your customers can uncover the next service they want most."
    action = "Want me to suggest the best ask for your business?"

    return join_paragraphs(intro, ask_line, idea, action)


def winback_eligible_message(intro, category, payload):
    days = payload.get("days_since_expiry")
    lapsed = payload.get("lapsed_customers_added_since_expiry")
    perf_dip = format_pct(payload.get("perf_dip_pct"))
    line = f"Your plan expired {int(days)} days ago and {int(lapsed)} lapsed customers are still warm." if days is not None and lapsed is not None else "A winback opportunity is open now."
    signal = f"This is a good time to recover lost customers, especially since performance is down {perf_dip}." if perf_dip else "This can help bring back returning business."
    action = "Can I help you send the winback message?"

    return join_paragraphs(intro, line, signal, action)


def ipl_match_today_message(intro, category, payload):
    match = payload.get("match") or "IPL match today"
    venue = payload.get("venue")
    time = payload.get("match_time_iso")
    match_line = f"{match} is happening today." if match else "There is a big match today."
    venue_line = f"It's a good day for {category_match_offer(category)}" if category else "This can be a strong promotional moment."
    action = "Would you like me to help make tonight a busy one?"

    return join_paragraphs(intro, match_line, venue_line, action)


def review_theme_emerged_message(intro, category, payload):
    theme = payload.get("theme") or "a customer concern"
    count = payload.get("occurrences_30d")
    quote = payload.get("common_quote")
    theme_name = theme.replace('_', ' ')
    count_line = f"{int(count)} reviews in the last 30 days mention {theme_name}." if count is not None else f"A review theme has emerged: {theme_name}."
    quote_line = f"Customers are saying: \"{quote}\"." if quote else "This is worth addressing quickly."
    action = "Want me to draft a response or a service fix note?"

    return join_paragraphs(intro, count_line, quote_line, action)


def milestone_reached_message(intro, category, payload):
    metric = payload.get("metric") or "reviews"
    current = payload.get("value_now")
    milestone = payload.get("milestone_value")
    if current is not None and milestone is not None:
        milestone_line = f"You have {int(current)} {metric.replace('_', ' ')}, {int(milestone - current)} away from {int(milestone)}." if current < milestone else f"You have crossed {int(milestone)} {metric.replace('_', ' ')}."
    else:
        milestone_line = f"You are close to a new {metric} milestone."

    action = "Should I help you celebrate this with a quick post or customer note?"
    return join_paragraphs(intro, milestone_line, action)


def active_planning_intent_message(intro, category, payload):
    intent = payload.get("intent_topic") or "a planning topic"
    last = payload.get("merchant_last_message")
    intent_line = f"You were already talking about {intent.replace('_', ' ')}." if intent else "There is an active planning intent in progress."
    follow = f"I can draft the next message based on your last note: {last}." if last else "I can draft the next step for you."
    action = "Shall I prepare that?"

    return join_paragraphs(intro, intent_line, follow, action)


def seasonal_perf_dip_message(intro, category, payload, performance):
    delta = format_pct(payload.get("delta_pct"))
    season_note = payload.get("season_note") or "seasonal demand shift"
    metric = payload.get("metric") or "performance"
    perf_line = f"Your {metric} is down {delta} during this seasonal window." if delta else f"Your {metric} is softer than usual this season."
    suggestion = seasonal_suggestion(category, season_note)
    action = "Want me to help you turn this season around?"

    return join_paragraphs(intro, perf_line, suggestion, action)


def customer_lapsed_hard_message(intro, category, payload):
    days = payload.get("days_since_last_visit")
    focus = payload.get("previous_focus")
    line = f"A customer has not returned in {int(days)} days after {focus.replace('_', ' ')}." if days is not None and focus else "A hard-lapsed customer is ready for a re-engagement attempt."
    action = "Can I draft the re-engagement message for you?"

    return join_paragraphs(intro, line, action)


def trial_followup_message(intro, category, payload):
    trial_date = payload.get("trial_date")
    option = first_slot_label(payload.get("next_session_options", []) or [])
    line = f"A trial client from {trial_date} is ready for the next session." if trial_date else "A trial follow-up is due now."
    option_line = f"I can offer them {option}." if option else "I can suggest the best next slot."
    action = "Shall I prepare the follow-up?"

    return join_paragraphs(intro, line, option_line, action)


def supply_alert_message(intro, category, payload):
    molecule = payload.get("molecule")
    batches = payload.get("affected_batches", []) or []
    manufacturer = payload.get("manufacturer")
    line = f"There is a supply alert for {molecule}." if molecule else "There is a medicine alert."
    batch_line = f"Affected batches: {format_list(batches)}." if batches else "Please review the affected stock."
    manuf_line = f"Manufacturer: {manufacturer}." if manufacturer else ""
    action = "Would you like help drafting a staff alert or supplier note?"

    return join_paragraphs(intro, line, batch_line, manuf_line, action)


def chronic_refill_due_message(intro, category, payload):
    molecules = payload.get("molecule_list") or []
    run_out = payload.get("stock_runs_out_iso")
    address = payload.get("delivery_address_saved")
    line = f"A customer needs a refill for {format_list(molecules)} by {run_out}." if molecules and run_out else "A chronic refill is due soon."
    delivery_line = "The delivery address is already saved." if address else "You can also offer home delivery."
    action = "Should I draft the reminder for this customer?"

    return join_paragraphs(intro, line, delivery_line, action)


def category_seasonal_message(intro, category, payload):
    season = payload.get("season") or "this season"
    trends = payload.get("trends", []) or []
    trend_line = f"Seasonal demand is shifting: {format_list(trends)}." if trends else f"There is a seasonal trend for {season}."
    action = "Can I help you use this to update your shelf or offer plan?"

    return join_paragraphs(intro, trend_line, action)


def gbp_unverified_message(intro, category, payload):
    uplift = payload.get("estimated_uplift_pct")
    line = "Your Google Business Profile is not verified yet." if payload.get("verified") is False else "Your GBP verification needs attention."
    uplift_line = f"Verification could improve visibility by around {format_pct(uplift)}." if uplift is not None else "Verifying it can help your local reach."
    action = "Would you like me to guide you through verification?"

    return join_paragraphs(intro, line, uplift_line, action)


def cde_opportunity_message(intro, category, payload):
    credits = payload.get("credits")
    fee = payload.get("fee")
    line = f"There is a CDE opportunity available for {credits} credits." if credits is not None else "A CDE opportunity is available."
    fee_line = f"The fee is {fee}." if fee else "It looks low-cost or free for members."
    action = "Should I help you sign up or share the details?"

    return join_paragraphs(intro, line, fee_line, action)


def competitor_opened_message(intro, category, payload):
    competitor = payload.get("competitor_name")
    distance = payload.get("distance_km")
    their_offer = payload.get("their_offer")
    comp_line = f"{competitor} opened nearby{f' ({distance} km)' if distance is not None else ''}." if competitor else "A new competitor is nearby."
    offer_line = f"They are promoting {their_offer}." if their_offer else "It is worth refreshing your offer."
    action = "Want me to help you respond with a strong local offer?"

    return join_paragraphs(intro, comp_line, offer_line, action)


def perf_spike_message(intro, category, payload, performance):
    metric = payload.get("metric") or "activity"
    delta_pct = format_pct(payload.get("delta_pct"))
    driver = payload.get("likely_driver")
    line = f"Your {metric} has jumped {delta_pct}." if delta_pct else f"Your {metric} is showing a strong spike."
    driver_line = f"This momentum looks driven by {driver.replace('_', ' ')}." if driver else "This is a good moment to amplify what is working."
    action = "Shall I help you capitalise on it?"

    return join_paragraphs(intro, line, driver_line, action)


def dormant_with_vera_message(intro, category, payload):
    days = payload.get("days_since_last_merchant_message")
    topic = payload.get("last_topic")
    line = f"We haven't reached out in {int(days)} days." if days is not None else "It has been a while since your last message."
    topic_line = f"The last topic was {topic.replace('_', ' ')}." if topic else "I can restart with a fresh, relevant note."
    action = "Can I draft the next message for you?"

    return join_paragraphs(intro, line, topic_line, action)


def fallback_message(intro, category, performance, signals, offers):
    perf_line = []
    if performance.get("views") is not None:
        perf_line.append(f"Your last 30 days show {int(performance.get('views'))} views")
    if performance.get("calls") is not None:
        perf_line.append(f"and {int(performance.get('calls'))} calls")
    perf_line = ", ".join(perf_line) + "." if perf_line else ""

    signal_line = "".join([f"The signal {signal.replace('_', ' ')} is on." for signal in signals[:1]])
    action = "Would you like me to suggest the best next step for your business?"

    return join_paragraphs(intro, perf_line, signal_line, action)


def first_active_offer(offers):
    for offer in offers:
        if offer.get("status") == "active" and offer.get("title"):
            return offer.get("title")
    return None


def first_slot_label(slots):
    for slot in slots:
        label = slot.get("label")
        if label:
            return label
    return None


def humanize_service(service):
    if not service:
        return "the service"
    text = service.replace("_", " ")
    text = text.replace("6 month", "6-month").replace("6 months", "6-month")
    return text


def format_pct(value, absolute=False):
    if value is None:
        return None
    try:
        pct = float(value)
    except (TypeError, ValueError):
        return None
    if absolute:
        pct = abs(pct)
    formatted = f"{pct * 100:.0f}%"
    return formatted if formatted.startswith("-") or formatted.startswith("+") else f"{formatted}"


def safe_keyword(value):
    if not value or not isinstance(value, str):
        return None
    return value.replace("-", " ").replace("_", " ")


def format_list(items):
    clean = [str(item) for item in items if item]
    if not clean:
        return ""
    if len(clean) == 1:
        return clean[0]
    if len(clean) == 2:
        return f"{clean[0]} and {clean[1]}"
    return ", ".join(clean[:-1]) + f" and {clean[-1]}"


def category_festival_suggestion(category, festival):
    if category == "dentists":
        return f"A {festival} wellness offer for regular check-ups or whitening can be compelling for local patients."
    if category == "salons":
        return f"A festive beauty package or bridal pre-wedding campaign would fit {festival} well."
    if category == "restaurants":
        return f"A special {festival} menu or delivery bundle can attract more orders."
    if category == "gyms":
        return f"A festival fitness challenge or new membership drive can help keep sign-ups steady."
    if category == "pharmacies":
        return f"Promoting seasonal essentials like sunscreen and immunity kits is a good {festival} plan."
    return f"A {festival} campaign can help you capture more local demand."


def category_match_offer(category):
    if category == "restaurants":
        return "an IPL meal bundle or delivery push"
    if category == "salons":
        return "a quick festive or party-ready package"
    if category == "gyms":
        return "a match-night recovery or training offer"
    if category == "pharmacies":
        return "a medicine or immunity offer for match-day families"
    return "a local promotion."


def seasonal_suggestion(category, season_note):
    if category == "gyms":
        return "It may help to promote summer onboarding or a 30-day fitness challenge."
    if category == "pharmacies":
        return "This is a good time to highlight ORS, sunscreen, and antifungal stock."
    if category == "restaurants":
        return "A summer bundle or weekday special can keep orders stable."
    if category == "salons":
        return "A limited-time beauty package can keep booking momentum through the slow season."
    if category == "dentists":
        return "A seasonal reminder for preventive care or recall visits can protect your pipeline."
    return f"A thoughtful offer tied to {season_note.replace('_', ' ')} should help."


def join_paragraphs(intro, *parts):
    lines = [intro.strip()]
    for part in parts:
        if part:
            text = part.strip()
            if text and text not in lines:
                lines.append(text)
    return "\n\n".join(lines)
