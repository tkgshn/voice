import React, { useContext, useEffect, useState } from "react";
import { useLocation } from "react-router";
import { ActionContext } from "../../hooks";
import { WebService } from "../../services";
import { Domain, oauthState, twitterOauthSecret } from "../../utils";

import "./Callback.scss";

function Callback() {
    const location = useLocation();
    const github_code = new URLSearchParams(location.search).get('code');
    const github_state = new URLSearchParams(location.search).get('state');
    const twitter_token = new URLSearchParams(location.search).get('oauth_token');
    const twitter_verifier = new URLSearchParams(location.search).get('oauth_verifier');
    const error_msg = new URLSearchParams(location.search).get('error');
    const error_description = new URLSearchParams(location.search).get('error_description');
    const { setUserData } = useContext(ActionContext);
    const [accessDenied, setAccessDenied] = useState(false);


    useEffect(() => {
      if (!github_code) {
        if (!twitter_token) {
          console.error("アクセス拒否：ユーザーがRxC Voiceに自分のTwitterアカウントへのアクセス許可を与えていない。");
          setAccessDenied(true);
        } else if (twitter_token !== oauthState) {
          if (error_msg && error_description) {
            console.error(error_msg + ": " + error_description);
          } else {
            console.error("Access Denied: Twitterトークンが無効です。");
          }
          setAccessDenied(true);
        } else {
          const params: any = {
            oauth_token: twitter_token,
            oauth_verifier: twitter_verifier,
            oauth_secret: twitterOauthSecret,
           }
          WebService.getTwitterAccessToken(params).subscribe(async (data) => {
            if (data.ok) {
              console.log("acquired twitter token");
              const userData = await data.json();
              setUserData(userData);
              window.location.href = Domain.WEB;
            } else {
              setAccessDenied(true);
            }
          });
        }
      } else {
        if (github_state !== oauthState) {
          console.error("アクセスが拒否されました。Github トークンが無効です.");
          setAccessDenied(true);
        } else {
          const params: any = { code: github_code, state: github_state, }
          WebService.verifyGithub(params).subscribe(async (data) => {
            if (data.ok) {
              console.log("取得済みgithubトークン");
              const userData = await data.json();
              setUserData(userData);
              window.location.href = Domain.WEB;
            } else {
              const error = await data.json();
              console.error(error);
              setAccessDenied(true);
            }
          });
        }
      }

     // eslint-disable-next-line react-hooks/exhaustive-deps
   }, []);

    return (
        <div className="validation-page">
          {accessDenied ? (
            <>
            <h2>アクセス拒否</h2>
            <p>RxC VoiceがあなたのGithubまたはTwitterアカウントへのアクセスを拒否したか、このリンクが壊れているか、有効期限が切れている可能性があります。</p>
            </>
          ) : (
            <h2>verifying your account...</h2>
          )}
        </div>
    );
}

export default Callback;
