

import re

from ..extractor.common import (
    InfoExtractor,
)
from ..extractor.pbs import (
    PBSIE
)

class Watch_Thirteen_IE(PBSIE):
    _STATIONS = (
        (r'(?:video|www|player)\.pbs\.org', 'PBS: Public Broadcasting Service'),  # http://www.pbs.org/
        (r'video\.aptv\.org', 'APT - Alabama Public Television (WBIQ)'),  # http://aptv.org/
        (r'video\.gpb\.org', 'GPB/Georgia Public Broadcasting (WGTV)'),  # http://www.gpb.org/
        (r'video\.mpbonline\.org', 'Mississippi Public Broadcasting (WMPN)'),  # http://www.mpbonline.org
        (r'video\.wnpt\.org', 'Nashville Public Television (WNPT)'),  # http://www.wnpt.org
        (r'video\.wfsu\.org', 'WFSU-TV (WFSU)'),  # http://wfsu.org/
        (r'video\.wsre\.org', 'WSRE (WSRE)'),  # http://www.wsre.org
        (r'video\.wtcitv\.org', 'WTCI (WTCI)'),  # http://www.wtcitv.org
        (r'video\.pba\.org', 'WPBA/Channel 30 (WPBA)'),  # http://pba.org/
        (r'video\.alaskapublic\.org', 'Alaska Public Media (KAKM)'),  # http://alaskapublic.org/kakm
        # (r'kuac\.org', 'KUAC (KUAC)'),  # http://kuac.org/kuac-tv/
        # (r'ktoo\.org', '360 North (KTOO)'),  # http://www.ktoo.org/
        # (r'azpm\.org', 'KUAT 6 (KUAT)'),  # http://www.azpm.org/
        (r'video\.azpbs\.org', 'Arizona PBS (KAET)'),  # http://www.azpbs.org
        (r'portal\.knme\.org', 'KNME-TV/Channel 5 (KNME)'),  # http://www.newmexicopbs.org/
        (r'video\.vegaspbs\.org', 'Vegas PBS (KLVX)'),  # http://vegaspbs.org/
        (r'watch\.aetn\.org', 'AETN/ARKANSAS ETV NETWORK (KETS)'),  # http://www.aetn.org/
        (r'video\.ket\.org', 'KET (WKLE)'),  # http://www.ket.org/
        (r'video\.wkno\.org', 'WKNO/Channel 10 (WKNO)'),  # http://www.wkno.org/
        (r'video\.lpb\.org', 'LPB/LOUISIANA PUBLIC BROADCASTING (WLPB)'),  # http://www.lpb.org/
        (r'videos\.oeta\.tv', 'OETA (KETA)'),  # http://www.oeta.tv
        (r'video\.optv\.org', 'Ozarks Public Television (KOZK)'),  # http://www.optv.org/
        (r'watch\.wsiu\.org', 'WSIU Public Broadcasting (WSIU)'),  # http://www.wsiu.org/
        (r'video\.keet\.org', 'KEET TV (KEET)'),  # http://www.keet.org
        (r'pbs\.kixe\.org', 'KIXE/Channel 9 (KIXE)'),  # http://kixe.org/
        (r'video\.kpbs\.org', 'KPBS San Diego (KPBS)'),  # http://www.kpbs.org/
        (r'video\.kqed\.org', 'KQED (KQED)'),  # http://www.kqed.org
        (r'vids\.kvie\.org', 'KVIE Public Television (KVIE)'),  # http://www.kvie.org
        (r'video\.pbssocal\.org', 'PBS SoCal/KOCE (KOCE)'),  # http://www.pbssocal.org/
        (r'video\.valleypbs\.org', 'ValleyPBS (KVPT)'),  # http://www.valleypbs.org/
        (r'video\.cptv\.org', 'CONNECTICUT PUBLIC TELEVISION (WEDH)'),  # http://cptv.org
        (r'watch\.knpb\.org', 'KNPB Channel 5 (KNPB)'),  # http://www.knpb.org/
        (r'video\.soptv\.org', 'SOPTV (KSYS)'),  # http://www.soptv.org
        # (r'klcs\.org', 'KLCS/Channel 58 (KLCS)'),  # http://www.klcs.org
        # (r'krcb\.org', 'KRCB Television & Radio (KRCB)'),  # http://www.krcb.org
        # (r'kvcr\.org', 'KVCR TV/DT/FM :: Vision for the Future (KVCR)'),  # http://kvcr.org
        (r'video\.rmpbs\.org', 'Rocky Mountain PBS (KRMA)'),  # http://www.rmpbs.org
        (r'video\.kenw\.org', 'KENW-TV3 (KENW)'),  # http://www.kenw.org
        (r'video\.kued\.org', 'KUED Channel 7 (KUED)'),  # http://www.kued.org
        (r'video\.wyomingpbs\.org', 'Wyoming PBS (KCWC)'),  # http://www.wyomingpbs.org
        (r'video\.cpt12\.org', 'Colorado Public Television / KBDI 12 (KBDI)'),  # http://www.cpt12.org/
        (r'video\.kbyueleven\.org', 'KBYU-TV (KBYU)'),  # http://www.kbyutv.org/
        (r'(?:video|watch)\.thirteen\.org', 'Thirteen/WNET New York (WNET)'),  # http://www.thirteen.org
        (r'video\.wgbh\.org', 'WGBH/Channel 2 (WGBH)'),  # http://wgbh.org
        (r'video\.wgby\.org', 'WGBY (WGBY)'),  # http://www.wgby.org
        (r'watch\.njtvonline\.org', 'NJTV Public Media NJ (WNJT)'),  # http://www.njtvonline.org/
        # (r'ripbs\.org', 'Rhode Island PBS (WSBE)'),  # http://www.ripbs.org/home/
        (r'watch\.wliw\.org', 'WLIW21 (WLIW)'),  # http://www.wliw.org/
        (r'video\.mpt\.tv', 'mpt/Maryland Public Television (WMPB)'),  # http://www.mpt.org
        (r'watch\.weta\.org', 'WETA Television and Radio (WETA)'),  # http://www.weta.org
        (r'video\.whyy\.org', 'WHYY (WHYY)'),  # http://www.whyy.org
        (r'video\.wlvt\.org', 'PBS 39 (WLVT)'),  # http://www.wlvt.org/
        (r'video\.wvpt\.net', 'WVPT - Your Source for PBS and More! (WVPT)'),  # http://www.wvpt.net
        (r'video\.whut\.org', 'Howard University Television (WHUT)'),  # http://www.whut.org
        (r'video\.wedu\.org', 'WEDU PBS (WEDU)'),  # http://www.wedu.org
        (r'video\.wgcu\.org', 'WGCU Public Media (WGCU)'),  # http://www.wgcu.org/
        # (r'wjct\.org', 'WJCT Public Broadcasting (WJCT)'),  # http://www.wjct.org
        (r'video\.wpbt2\.org', 'WPBT2 (WPBT)'),  # http://www.wpbt2.org
        (r'video\.wucftv\.org', 'WUCF TV (WUCF)'),  # http://wucftv.org
        (r'video\.wuft\.org', 'WUFT/Channel 5 (WUFT)'),  # http://www.wuft.org
        (r'watch\.wxel\.org', 'WXEL/Channel 42 (WXEL)'),  # http://www.wxel.org/home/
        (r'video\.wlrn\.org', 'WLRN/Channel 17 (WLRN)'),  # http://www.wlrn.org/
        (r'video\.wusf\.usf\.edu', 'WUSF Public Broadcasting (WUSF)'),  # http://wusf.org/
        (r'video\.scetv\.org', 'ETV (WRLK)'),  # http://www.scetv.org
        (r'video\.unctv\.org', 'UNC-TV (WUNC)'),  # http://www.unctv.org/
        # (r'pbsguam\.org', 'PBS Guam (KGTF)'),  # http://www.pbsguam.org/
        (r'video\.pbshawaii\.org', 'PBS Hawaii - Oceanic Cable Channel 10 (KHET)'),  # http://www.pbshawaii.org/
        (r'video\.idahoptv\.org', 'Idaho Public Television (KAID)'),  # http://idahoptv.org
        (r'video\.ksps\.org', 'KSPS (KSPS)'),  # http://www.ksps.org/home/
        (r'watch\.opb\.org', 'OPB (KOPB)'),  # http://www.opb.org
        (r'watch\.nwptv\.org', 'KWSU/Channel 10 & KTNW/Channel 31 (KWSU)'),  # http://www.kwsu.org
        (r'video\.will\.illinois\.edu', 'WILL-TV (WILL)'),  # http://will.illinois.edu/
        (r'video\.networkknowledge\.tv', 'Network Knowledge - WSEC/Springfield (WSEC)'),  # http://www.wsec.tv
        (r'video\.wttw\.com', 'WTTW11 (WTTW)'),  # http://www.wttw.com/
        # (r'wtvp\.org', 'WTVP & WTVP.org, Public Media for Central Illinois (WTVP)'),  # http://www.wtvp.org/
        (r'video\.iptv\.org', 'Iowa Public Television/IPTV (KDIN)'),  # http://www.iptv.org/
        (r'video\.ninenet\.org', 'Nine Network (KETC)'),  # http://www.ninenet.org
        (r'video\.wfwa\.org', 'PBS39 Fort Wayne (WFWA)'),  # http://wfwa.org/
        (r'video\.wfyi\.org', 'WFYI Indianapolis (WFYI)'),  # http://www.wfyi.org
        (r'video\.mptv\.org', 'Milwaukee Public Television (WMVS)'),  # http://www.mptv.org
        (r'video\.wnin\.org', 'WNIN (WNIN)'),  # http://www.wnin.org/
        (r'video\.wnit\.org', 'WNIT Public Television (WNIT)'),  # http://www.wnit.org/
        (r'video\.wpt\.org', 'WPT (WPNE)'),  # http://www.wpt.org/
        (r'video\.wvut\.org', 'WVUT/Channel 22 (WVUT)'),  # http://wvut.org/
        (r'video\.weiu\.net', 'WEIU/Channel 51 (WEIU)'),  # http://www.weiu.net
        (r'video\.wqpt\.org', 'WQPT-TV (WQPT)'),  # http://www.wqpt.org
        (r'video\.wycc\.org', 'WYCC PBS Chicago (WYCC)'),  # http://www.wycc.org
        # (r'lakeshorepublicmedia\.org', 'Lakeshore Public Television (WYIN)'),  # http://lakeshorepublicmedia.org/
        (r'video\.wipb\.org', 'WIPB-TV (WIPB)'),  # http://wipb.org
        (r'video\.indianapublicmedia\.org', 'WTIU (WTIU)'),  # http://indianapublicmedia.org/tv/
        (r'watch\.cetconnect\.org', 'CET  (WCET)'),  # http://www.cetconnect.org
        (r'video\.thinktv\.org', 'ThinkTVNetwork (WPTD)'),  # http://www.thinktv.org
        (r'video\.wbgu\.org', 'WBGU-TV (WBGU)'),  # http://wbgu.org
        (r'video\.wgvu\.org', 'WGVU TV (WGVU)'),  # http://www.wgvu.org/
        (r'video\.netnebraska\.org', 'NET1 (KUON)'),  # http://netnebraska.org
        (r'video\.pioneer\.org', 'Pioneer Public Television (KWCM)'),  # http://www.pioneer.org
        (r'watch\.sdpb\.org', 'SDPB Television (KUSD)'),  # http://www.sdpb.org
        (r'video\.tpt\.org', 'TPT (KTCA)'),  # http://www.tpt.org
        (r'watch\.ksmq\.org', 'KSMQ (KSMQ)'),  # http://www.ksmq.org/
        (r'watch\.kpts\.org', 'KPTS/Channel 8 (KPTS)'),  # http://www.kpts.org/
        (r'watch\.ktwu\.org', 'KTWU/Channel 11 (KTWU)'),  # http://ktwu.org
        # (r'shptv\.org', 'Smoky Hills Public Television (KOOD)'),  # http://www.shptv.org
        # (r'kcpt\.org', 'KCPT Kansas City Public Television (KCPT)'),  # http://kcpt.org/
        # (r'blueridgepbs\.org', 'Blue Ridge PBS (WBRA)'),  # http://www.blueridgepbs.org/
        (r'watch\.easttennesseepbs\.org', 'East Tennessee PBS (WSJK)'),  # http://easttennesseepbs.org
        (r'video\.wcte\.tv', 'WCTE-TV (WCTE)'),  # http://www.wcte.org
        (r'video\.wljt\.org', 'WLJT, Channel 11 (WLJT)'),  # http://wljt.org/
        (r'video\.wosu\.org', 'WOSU TV (WOSU)'),  # http://wosu.org/
        (r'video\.woub\.org', 'WOUB/WOUC (WOUB)'),  # http://woub.org/tv/index.php?section=5
        (r'video\.wvpublic\.org', 'WVPB (WVPB)'),  # http://wvpublic.org/
        (r'video\.wkyupbs\.org', 'WKYU-PBS (WKYU)'),  # http://www.wkyupbs.org
        # (r'wyes\.org', 'WYES-TV/New Orleans (WYES)'),  # http://www.wyes.org
        (r'video\.kera\.org', 'KERA 13 (KERA)'),  # http://www.kera.org/
        (r'video\.mpbn\.net', 'MPBN (WCBB)'),  # http://www.mpbn.net/
        (r'video\.mountainlake\.org', 'Mountain Lake PBS (WCFE)'),  # http://www.mountainlake.org/
        (r'video\.nhptv\.org', 'NHPTV (WENH)'),  # http://nhptv.org/
        (r'video\.vpt\.org', 'Vermont PBS (WETK)'),  # http://www.vpt.org
        (r'video\.witf\.org', 'witf (WITF)'),  # http://www.witf.org
        (r'watch\.wqed\.org', 'WQED Multimedia (WQED)'),  # http://www.wqed.org/
        (r'video\.wmht\.org', 'WMHT Educational Telecommunications (WMHT)'),  # http://www.wmht.org/home/
        (r'video\.deltabroadcasting\.org', 'Q-TV (WDCQ)'),  # http://www.deltabroadcasting.org
        (r'video\.dptv\.org', 'WTVS Detroit Public TV (WTVS)'),  # http://www.dptv.org/
        (r'video\.wcmu\.org', 'CMU Public Television (WCMU)'),  # http://www.wcmu.org
        (r'video\.wkar\.org', 'WKAR-TV (WKAR)'),  # http://wkar.org/
        (r'wnmuvideo\.nmu\.edu', 'WNMU-TV Public TV 13 (WNMU)'),  # http://wnmutv.nmu.edu
        (r'video\.wdse\.org', 'WDSE - WRPT (WDSE)'),  # http://www.wdse.org/
        (r'video\.wgte\.org', 'WGTE TV (WGTE)'),  # http://www.wgte.org
        (r'video\.lptv\.org', 'Lakeland Public Television (KAWE)'),  # http://www.lakelandptv.org
        # (r'prairiepublic\.org', 'PRAIRIE PUBLIC (KFME)'),  # http://www.prairiepublic.org/
        (r'video\.kmos\.org', 'KMOS-TV - Channels 6.1, 6.2 and 6.3 (KMOS)'),  # http://www.kmos.org/
        (r'watch\.montanapbs\.org', 'MontanaPBS (KUSM)'),  # http://montanapbs.org
        (r'video\.krwg\.org', 'KRWG/Channel 22 (KRWG)'),  # http://www.krwg.org
        (r'video\.kacvtv\.org', 'KACV (KACV)'),  # http://www.panhandlepbs.org/home/
        (r'video\.kcostv\.org', 'KCOS/Channel 13 (KCOS)'),  # www.kcostv.org
        (r'video\.wcny\.org', 'WCNY/Channel 24 (WCNY)'),  # http://www.wcny.org
        (r'video\.wned\.org', 'WNED (WNED)'),  # http://www.wned.org/
        (r'watch\.wpbstv\.org', 'WPBS (WPBS)'),  # http://www.wpbstv.org
        (r'video\.wskg\.org', 'WSKG Public TV (WSKG)'),  # http://wskg.org
        (r'video\.wxxi\.org', 'WXXI (WXXI)'),  # http://wxxi.org
        (r'video\.wpsu\.org', 'WPSU (WPSU)'),  # http://www.wpsu.org
        # (r'wqln\.org', 'WQLN/Channel 54 (WQLN)'),  # http://www.wqln.org
        (r'on-demand\.wvia\.org', 'WVIA Public Media Studios (WVIA)'),  # http://www.wvia.org/
        (r'video\.wtvi\.org', 'WTVI (WTVI)'),  # http://www.wtvi.org/
        # (r'whro\.org', 'WHRO (WHRO)'),  # http://whro.org
        (r'video\.westernreservepublicmedia\.org', 'Western Reserve PBS (WNEO)'),  # http://www.WesternReservePublicMedia.org/
        (r'video\.ideastream\.org', 'WVIZ/PBS ideastream (WVIZ)'),  # http://www.wviz.org/
        (r'video\.kcts9\.org', 'KCTS 9 (KCTS)'),  # http://kcts9.org/
        (r'video\.basinpbs\.org', 'Basin PBS (KPBT)'),  # http://www.basinpbs.org
        (r'video\.houstonpbs\.org', 'KUHT / Channel 8 (KUHT)'),  # http://www.houstonpublicmedia.org/
        # (r'tamu\.edu', 'KAMU - TV (KAMU)'),  # http://KAMU.tamu.edu
        # (r'kedt\.org', 'KEDT/Channel 16 (KEDT)'),  # http://www.kedt.org
        (r'video\.klrn\.org', 'KLRN (KLRN)'),  # http://www.klrn.org
        (r'video\.klru\.tv', 'KLRU (KLRU)'),  # http://www.klru.org
        # (r'kmbh\.org', 'KMBH-TV (KMBH)'),  # http://www.kmbh.org
        # (r'knct\.org', 'KNCT (KNCT)'),  # http://www.knct.org
        # (r'ktxt\.org', 'KTTZ-TV (KTXT)'),  # http://www.ktxt.org
        (r'video\.wtjx\.org', 'WTJX Channel 12 (WTJX)'),  # http://www.wtjx.org/
        (r'video\.ideastations\.org', 'WCVE PBS (WCVE)'),  # http://ideastations.org/
        (r'video\.kbtc\.org', 'KBTC Public Television (KBTC)'),  # http://kbtc.org
    )

    _VALID_URL = r'''(?x)(?:https?:)?//
        (?:
           # Direct video URL
           (?:%s)/(?:viralplayer|video)/(?P<id>[0-9]+)/? |
           # Article with embedded player (or direct video)
           (?:www\.)?pbs\.org/(?:[^/]+/){2,5}(?P<presumptive_id>[^/]+?)(?:\.html)?/?(?:$|[?\#]) |
           # Player
           (?:video|player)\.pbs\.org/(?:widget/)?partnerplayer/(?P<player_id>[^/]+)/
        )
    ''' % '|'.join(list(zip(*_STATIONS))[0])