import React from "react";
import { Link } from "react-router-dom";
import slugify from "react-slugify";
import defaultPic from '../../../../../../assets/profile_icon.svg';

import "./DelegateCard.scss";

function DelegateCard(props: any) {

  return (
    <li className="delegate-card" key={props.delegate.id} >
      {props.delegate.profile_pic ? (
        <img src={props.delegate.profile_pic} className="profile-pic" alt="profile-pic" />
      ) : (
        <img src={defaultPic} className="profile-pic" alt="profile-pic" />
      )}
      <div className="info">
        <h3 className="name">{props.delegate.user.first_name + " " + props.delegate.user.last_name}</h3>
        <h3 className="email">{props.delegate.user.email}</h3>
        <h3 className="credit-balance">Credit Balance: {props.delegate.credit_balance}</h3>
      </div>
      <Link
      to={`/${props.process.id}/${slugify(props.process.title)}/give-credits`}
      className="give-credits"
      >
      give credits
      </Link>
    </li>
  );
}

export default DelegateCard;
