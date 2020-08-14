url="registry.cn-hangzhou.aliyuncs.com"
namespace="tinyedge"
module_name="mqtt-connector"
architecture="arm32"
version="v1.0"
docker build -t $module_name .
docker tag $module_name $url/$namespace/$module_name:$architecture-$version
docker tag $module_name $url/$namespace/$module_name
docker tag $module_name $url/$namespace/$module_name:$version
docker push $url/$namespace/$module_name:$architecture-$version
