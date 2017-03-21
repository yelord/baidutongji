<?php
require_once('../../lib/thirdparty/mcpack-hessian/HessianClient.php');

try {
    $url = 'http://localhost:8848/service/tongji/dradapter';
    $proxy = new HessianClient($url);
    
    $user = array('opUser' => 0, 'dataUser' => 5763585);
    
    // get site list
    $ret = $proxy->getSiteList($user, array(), null);
    print_r($ret);
    
    $siteList = $ret['data'][0]['list'];
    if (count($siteList) > 0) {
        $siteId = $siteList[0]['site_id'];
        // get data
        $request = array(
            'site_id' => $siteId,                   //站点ID
            'method' => 'trend/time/a',             //趋势分析报告
            'start_date' => '20160501',             //所查询数据的起始日期
            'end_date' => '20160531',               //所查询数据的结束日期
            'metrics' => 'pv_count,visitor_count',  //所查询指标为PV和UV
            'max_results' => 0,                     //返回所有条数
            'gran' => 'day',                        //按天粒度
        );
        $ret = $proxy->getData($user, $request, null);
        print_r($ret);
    }
}
catch (Exception $ex) {
    echo $ex->getMessage() . PHP_EOL;
}