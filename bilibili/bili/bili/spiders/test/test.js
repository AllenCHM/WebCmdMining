(function (global, undefined) {
    "use strict";
    global.oneHundredThousandFormat = function (num) {
        Object.prototype.toString.call(num) === "[object String]" ? void 0 : num = num.toString();
        if (num.indexOf("万") > -1) {
            var pureNum = parseFloat(num.substr(0, num.indexOf("万")));
            if (pureNum < 10)return num;
            var returnNum = pureNum.toFixed(1);
            return returnNum + "万"
        } else {
            if (parseInt(num, 10) < 1e5)return num
        }
        if (!(0 <= num.indexOf("万") || 0 <= num.indexOf(","))) {
            return (num = parseInt(num)) ? 1e4 <= num && (num = (num / 1e4).toFixed(1) + "万") : num = "--", num
        }
    };
    var settings = {};
    settings.publicURL = "http://static.hdslb.com/live-static/";
    settings.cookieSyllable = "DedeUserID";
    settings.scriptToLoad = {
        common: [settings.publicURL + "js/live.room.min.js"],
        admin: [settings.publicURL + "js/live.admin.new.js"],
        redactor: [settings.publicURL + "js/redactor-8.2.4.js", settings.publicURL + "js/redactor-8.2.4.zh_cn.js", settings.publicURL + "js/fullscreen.js"]
    };
    settings.errorHint = {};
    settings.errorHint.common = "Bilibili Live: 页面载入出现错误，请尝试刷新页面，若依旧出现问题，请联系 Bilibili 工作人员! :) \n  - Error Detail: ";
    settings.errorHint = {
        typeError: settings.errorHint.common + "房间信息请求不成功或数据错误.",
        missingData: settings.errorHint.common + "必要数据丢失."
    };
    var $body = $("body"), $liveStatusBtn = $("#live_status_control");
    var initReqFunction = {
        playerInit: function () {
            if (navigator.userAgent.match(/iPad/i) != null || navigator.userAgent.match(/iPhone/i) != null || navigator.userAgent.match(/iPod/i) != null || navigator.userAgent.match(/MicroMessenger/i) != null || navigator.userAgent.match(/Windows Phone/i) != null || navigator.userAgent.match(/Android/i) != null || location.hash == "#html5") {
                $.ajax({
                    url: "/api/h5playurl?roomid=" + global.ROOMID, dataType: "jsonp", success: function (res) {
                        if (typeof res["durl"][0].url == "undefined") {
                            return
                        }
                        window.html5data = res["durl"][0];
                        window.html5data.src = res["durl"][0].url;
                        window.html5data.img = global.COVER;
                        window.html5data.live = true;
                        window.html5data.cid = "ws://wschat.bilibili.com:8088/" + global.ROOMID;
                        $.ajaxSetup({cache: true});
                        $("#player-container").html('                        <link type="text/css" href="http://static.hdslb.com/css/simple.min.css" rel="stylesheet" />                        <script type="text/javascript" src="http://static.hdslb.com/js/simple.min.js"></script>').css("width", "100%").css("height", "100%").attr("id", "bofqi")
                    }
                })
            } else {
                global.liveBannerFunc = {};
                global.liveBannerFunc.onready = function () {
                }
            }
        }, setLiveStatus: function (liveStatus) {
            if (liveStatus === "on") {
                $liveStatusBtn.removeClass("off").addClass("on").children(".text").text("直播中")
            } else {
                $liveStatusBtn.removeClass("on").addClass("off").children(".text").text("准备中")
            }
            $liveStatusBtn.addClass("guest")
        }, update: [function giftTop(data) {
            var list = data.data.GIFT_TOP;
            for (var i = 0, length = list.length; i < length; i++) {
                var rank = "rank" + (i + 1), username = list[i].uname, coin = list[i].coin;
                var liDom = "<li><span class='fan-name " + rank + "'>" + username + "</span><span class='fan-support'>" + coin + "</span></li>";
                $("#ranking").append(liDom)
            }
        }, function fansCount(data) {
            $(".fans-count-num").text(global.oneHundredThousandFormat(data.data.FANS_COUNT)).attr("data-fans", data.data.FANS_COUNT)
        }, function giftCount(data) {
            var $giftNum = $(".giftsnum");
            $giftNum.text(global.setNum(global.oneHundredThousandFormat(data.data.RCOST), $giftNum))
        }, function starRank(data) {
            var $starRank = $(".live-controls .star-rank .data-count");
            if (data.data.starRank == false) {
                data.data.starRank = 0
            }
            $starRank.text(global.setNum(global.oneHundredThousandFormat(data.data.starRank), $starRank))
        }, function fffBurningIndex(data) {
            var $burningIndex = $(".fff-burning-index .data-count");
            data.data.FFF ? $burningIndex.text(global.setNum(global.oneHundredThousandFormat(data.data.FFF), $burningIndex)) : $burningIndex.text(0)
        }, function showNecessaryDom(data) {
            if (global.ISGETREGSILVER != 1) {
                $("#getFree").removeClass("dp-none")
            }
        }, function buyVIP() {
            var $vip = $(".receive .to-vip font");
            if (global.VIP == 1) {
                $vip.text("续费")
            } else {
                $vip.text("成为老爷")
            }
            $(".to-vip").on("click", function () {
                window.liveQuickLogin();
                window.open("/i#to-vip")
            })
        }, function seedsNum() {
            setTimeout(function () {
                global.setNum(global.formatFriendlyNumber(global.GOLD), $("#goldenseed-num"));
                global.setNum(global.formatFriendlyNumber(global.SILVER), $("#guazi-num"))
            }, 500)
        }, function fansMedal(data) {
            $(".medal-btn .tip-text").on("click", function (event) {
                event.preventDefault();
                event.stopPropagation();
                window.liveQuickLogin();
                global.fansMedal.getMyWearMedal();
                $(".current-medal-tip-box").fadeIn("fast")
            });
            $(".medal-btn").on("click", function (event) {
                event.stopPropagation()
            });
            $(document).on("click", function () {
                $(".current-medal-tip-box").fadeOut("fast");
                $(".medal-btn .choose-medal").hide()
            });
            $(".chat-room").on("hover", ".talk .medal-icon", function (event) {
                event.preventDefault();
                var parentOffset = $(this).offset();
                var scrollTop = $(document).scrollTop();
                var scrollLeft = $(document).scrollLeft();
                var $nowMedalInfo = $(this).find(".medal-info");
                $nowMedalInfo.css({top: parentOffset.top - scrollTop - 38, left: parentOffset.left - scrollLeft})
            })
        }, function setFansRanking(data) {
            $(".tabs").on("click", ".tab-fans-ranking", function (event) {
                global.fansMedal.loadFansRanking(data.data.ROOMID)
            })
        }, function setAdminList(data) {
            $(".tabs").on("click", ".tab-admin-list", function (event) {
                $.ajax({
                    url: "/liveact/ajaxGetAdminList",
                    type: "post",
                    data: {roomid: data.data.ROOMID},
                    dataType: "json",
                    success: function (result) {
                        if (result.code == 0 && result.data.length) {
                            var listData = result.data;
                            var $adminListContainer = $("#admin-list");
                            $adminListContainer.empty();
                            (function () {
                                for (var i = 0, length = listData.length; i < length; i++) {
                                    var listItem = '<li class="admin-list">' + '<a href="http://space.bilibili.com/' + listData[i].uid + '" target="_blank" class="admin-list-link">' + '<span class="admin-list-icon">房管</span><span title="进入 ' + listData[i].userinfo.uname + ' 的个人中心" class="admin-list-username">' + listData[i].userinfo.uname + "</span>" + "</a></li>";
                                    $adminListContainer.append(listItem)
                                }
                            })()
                        }
                    }
                })
            })
        }, function userLevel() {
            if (document.cookie.indexOf("DedeUserID") >= 0) {
                setInterval(function () {
                    $.ajax({
                        url: "/User/userOnlineHeart", type: "post", dataType: "json", success: function (result) {
                        }
                    })
                }, 3e5)
            }
            $(".chat-room").on("hover", ".talk .user-level-icon", function (event) {
                event.preventDefault();
                var parentOffset = $(this).offset();
                var scrollTop = $(document).scrollTop();
                var scrollLeft = $(document).scrollLeft();
                var $nowUserLevelInfo = $(this).find(".user-level-info");
                $nowUserLevelInfo.css({top: parentOffset.top - scrollTop - 68, left: parentOffset.left - scrollLeft})
            })
        }, function userLevel() {
            $(".chat-room").on("click", ".close-vip-tip-link", function (event) {
                event.preventDefault();
                var closeVipTipPopup = new CenterPopup({
                    content: '<div class="close-vip-tip-popup-wrap">' + "<h3 style='color: #4fc1e9; font-size: 20px;'>关闭老爷提示</h3>" + "<div>" + "<p>点击确认，可以关闭自己进入直播间的提示，关闭后可在直播个人中心重新开启提示功能哦(●′ω`●)~</p>" + "</div>" + '<div style="text-align: center"><button class="tip-primary close-vip-tip-popup-btn-ok" style="padding: 5px 25px; margin: 10px 10px 0;">确认</button><button class="tip-secondary close-vip-tip-popup-btn-cancel" style="padding: 5px 25px; margin: 10px 10px 0;">取消</button></div>' + "</div>",
                    width: 200,
                    closable: true
                });
                closeVipTipPopup.show({radius: true});
                $(".close-vip-tip-popup-btn-ok", closeVipTipPopup.el).on("click", function () {
                    $.ajax({
                        url: "/i/ajaxSetVipViewStatus",
                        type: "POST",
                        data: {status: 0},
                        dataType: "json",
                        success: function (result) {
                            if (result.code == 0) {
                                closeVipTipPopup.hide()
                            }
                        }
                    })
                });
                $(".close-vip-tip-popup-btn-cancel", closeVipTipPopup.el).on("click", function () {
                    closeVipTipPopup.hide()
                })
            })
        }]
    };
    var masterFunction = {
        update: [function showAdminDoms() {
            $(".link-container .admins").removeClass("dp-none");
            $(".live-admin > .tabs > .tab[data-target=blacklist-setting]").addClass("active border-top-none").removeClass("dp-none");
            $("#blacklist-setting").css({display: "block"})
        }], commonExec: function () {
            $body.append('<link rel="stylesheet" href="http://static.hdslb.com/css/redactor-8.2.4.css">');
            $body.append('<link rel="stylesheet" href="http://static.hdslb.com/live-static/css/adminRoom.css">');
            (function () {
                for (var i = 0, length = settings.scriptToLoad.admin.length; i < length; i++) {
                    (function (j) {
                        var len = length;
                        $.getScript(settings.scriptToLoad.admin[j], function () {
                            if (j === len - 1) {
                                (function () {
                                    for (var i = 0, length = masterFunction.update.length; i < length; i++) {
                                        masterFunction.update[i]()
                                    }
                                })();
                                global.ISANCHOR === 1 ? anchorFunction.request() : 0
                            }
                        })
                    })(i)
                }
            })()
        }
    };
    var anchorFunction = {
        request: function () {
            $.get("/live/getMasterInfo?roomid=" + ROOMID, {timestamp: Date.now()}, anchorFunction.callback, "JSON")
        }, update: [function showAdminDoms() {
            $(".link-container .settings").removeClass("dp-none");
            $(".live-admin > .tabs > .tab").removeClass("dp-none border-top-none active");
            $(".live-admin > .tabs > .tab[data-target=admin-setting]").addClass("active");
            $("#admin-setting").css({display: "block"});
            $("#blacklist-setting").css({display: "none"});
            $(".background-change").removeClass("dp-none")
        }, function redactorInit() {
            function secondLoad() {
                $.getScript(settings.scriptToLoad.redactor[1], function () {
                    $("#editor").redactor({
                        lang: "zh_cn",
                        minHeight: 125,
                        autoresize: false,
                        buttons: ["html", "formatting", "bold", "italic", "deleted", "unorderedlist", "orderedlist", "outdent", "indent", "file", "table", "link", "fontcolor", "backcolor", "alignment", "horizontalrule"]
                    })
                })
            }

            $.getScript(settings.scriptToLoad.redactor[0], secondLoad)
        }, function rejectDetect(data) {
            var denyData = data.data.deny;
            if (denyData == false) {
                return false
            }
            var subText = [];
            for (var i in denyData) {
                if (denyData[i] == -1) {
                    $(".live-room .reject").removeClass("dp-none");
                    var hintText = $(".live-room .reject .content").text();
                    switch (i) {
                        case"title":
                            subText.push("标题");
                            break;
                        case"description":
                            subText.push("简介");
                            break;
                        case"tags":
                            subText.push("标签");
                            break
                    }
                }
            }
            $(".live-room .reject .content").text(hintText + subText.join("、"))
        }, function updateLiveStatus() {
            $liveStatusBtn.removeClass("guest")
        }], auditExec: function (data) {
            if (data.data.audit) {
                var audit = data.data.audit;
                if (audit.titleInfo.status == 1) {
                    $(".head-title span").text(audit.titleInfo.msg).addClass("audit")
                }
                if (audit.descriptionInfo.status == 1) {
                    $("#live_desc").html(audit.descriptionInfo.msg).addClass("audit")
                }
                $("#name").attr("value", audit.titleInfo.msg);
                $("#editor").attr("value", audit.descriptionInfo.msg);
                (function () {
                    var $tagList = $(".head-tags .tag-list"), $adminTagList = $(".tags.form-control");
                    $tagList.empty();
                    $adminTagList.children("a").remove();
                    for (var j = 0, length = audit.tagsInfo.length; j < length; j++) {
                        var tagText = audit.tagsInfo[j].tag, auditStatus = "";
                        audit.tagsInfo[j].status == 1 ? auditStatus = "audit" : 0;
                        var liDom = '<li title="' + tagText + '"><a class="' + auditStatus + '" href="/search/index?keyword=' + tagText + '">' + tagText + "</a></li>";
                        $tagList.append(liDom);
                        var aDom = '<a href="javascript:void(0)" class="tag-block">' + tagText + "</a>";
                        $adminTagList.children(".tag-input").before(aDom)
                    }
                })()
            }
            var $template = $("#template"), templateID = parseInt(data.data.template, 10);
            $template.attr("data-value", templateID);
            switch (templateID) {
                case 1:
                    $template.text("游戏模板");
                    break;
                case 2:
                    $template.text("娱乐模板");
                    break
            }
            var $area = $("#area"), areaData = data.data.area;
            $area.attr("data-value", areaData.id);
            $area.text(areaData.name);
            $(".link-container .settings").on("click", function () {
                if ($(this).attr("inited") == "true") {
                    return false
                } else {
                    $(this).attr("inited", "true");
                    $(".select").iSelect(loadTags);
                    global.tags = new Tags($(".tags"))
                }
            })
        }, callback: function (data) {
            if (data.code != 0) {
                return false
            }
            anchorFunction.auditExec(data);
            (function () {
                for (var i = 0, length = anchorFunction.update.length; i < length; i++) {
                    anchorFunction.update[i](data)
                }
            })()
        }
    };
    var initRequest = {
        exec: function () {
            $(function () {
                $.get("/live/getInfo?roomid=" + global.ROOMID, initRequest.initReqCallback, "JSON")
            })
        }, initReqCallback: function (data) {
            (function () {
                for (var i in data.data) {
                    global[i] = data.data[i]
                }
            })();
            (function () {
                for (var i = 0, length = settings.scriptToLoad.common.length; i < length; i++) {
                    (function (j) {
                        var len = length;
                        $.getScript(settings.scriptToLoad.common[j], function () {
                            if (j === len - 1) {
                                initReqFunction.playerInit();
                                initReqFunction.setLiveStatus(data.data._status);
                                (function () {
                                    for (var k = 0, LENGTH = initReqFunction.update.length; k < LENGTH; k++) {
                                        initReqFunction.update[k](data)
                                    }
                                })();
                                if (data.data.ISADMIN === 1) {
                                    masterFunction.commonExec()
                                }
                                if (data.data.ISADMIN != 1) {
                                    $(".live-admin").add(".live-setting").remove()
                                }
                                $.getScript(settings.publicURL + "js/live.room.quiz.min.js")
                            }
                        })
                    })(i)
                }
            })()
        }
    };
    initRequest.exec()
})(window);