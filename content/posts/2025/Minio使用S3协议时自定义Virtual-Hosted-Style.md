---
title: Minio使用S3协议时自定义Virtual Hosted Style
date: '2025-11-21T21:02:12+08:00'
tags:
- Go
categories:
- 问题
draft: false
hiddenFromHomePage: false
hiddenFromSearch: false
---
# Minio使用S3协议时自定义Virtual Hosted Style

遇到一个minio使用COS作为s3存储时，多出来一个桶名路径的问题。本来以为是配置项的问题，各种方式填了个遍还是不行。最后狠下新来读源码，发现minio在构造请求url时有`virtual host style`和`path style`两种方式：

```go
    urlStr := scheme + "://" + host + "/"

    // Make URL only if bucketName is available, otherwise use the
    // endpoint URL.
    if bucketName != "" {
        // If endpoint supports virtual host style use that always.
        // Currently only S3 and Google Cloud Storage would support
        // virtual host style.
        if isVirtualHostStyle {
            urlStr = scheme + "://" + bucketName + "." + host + "/"
            if objectName != "" {
                urlStr += s3utils.EncodePath(objectName)
            }
        } else {
            // If not fall back to using path style.
            urlStr = urlStr + bucketName + "/"
            if objectName != "" {
                urlStr += s3utils.EncodePath(objectName)
            }
        }
    }
```

其中前者是`bucketName.host`的形式，即COS的形式，后者是`host/bucketName`。COS没有被识别成前者，就按照后者构造成了 `bucketName.host/bucketName`，额外的bucketName就被当作了文件路径。

找到了原因就该尝试着手修复，`isVirtualHostStyle`的判断如下：

```go
// returns true if virtual hosted style requests are to be used.
func (c *Client) isVirtualHostStyleRequest(url url.URL, bucketName string) bool {
    if c.lookupFn != nil {
        lookup := c.lookupFn(url, bucketName)
        switch lookup {
        case BucketLookupDNS:
            return true
        case BucketLookupPath:
            return false
        }
        // if its auto then we fallback to default detection.
        return s3utils.IsVirtualHostSupported(url, bucketName)
    }

    if bucketName == "" {
        return false
    }

    if c.lookup == BucketLookupDNS {
        return true
    }

    if c.lookup == BucketLookupPath {
        return false
    }

    // default to virtual only for Amazon/Google storage. In all other cases use
    // path style requests
    return s3utils.IsVirtualHostSupported(url, bucketName)
}
```

大致捋一下逻辑，首先通过`lookupFn`这个自定义的判断函数去判断类型，然后看是否存在预设值`lookup`，最后使用minio内置的`IsVirtualHostSupported`函数去判断类型。具体实现就是判断url中有没有AWS/Google/阿里云OSS的域名，在此不作展开。

可以看到，minio已经预留了lookupFn函数和lookup值用于二次开发。而我们只需要实现lookupFn函数，在创建client时传入就行：

```go
    client, err := minio.New(endpoint, &minio.Options{
        Creds:  credentials.NewStaticV4(accessKey, secretKey, ""),
        Secure: secure,
        Region: region,
        BucketLookupViaURL: CustomBucketLookupViaURL,
    })


// IsTencentCOSEndpoint - Match if it is exactly Tencent Cloud COS endpoint.
func IsTencentCOSEndpoint(endpointURL url.URL) bool {
    hostname := endpointURL.Hostname()

    return strings.HasSuffix(hostname, "myqcloud.com") ||
        strings.HasSuffix(hostname, "tencentcos.cn")
}

// CustomBucketLookupViaURL implements minio.BucketLookupViaURL function.
func CustomBucketLookupViaURL(endpointURL url.URL, bucketName string) minio.BucketLookupType {
    // 腾讯云COS支持VirtualHostStyle
    if IsTencentCOSEndpoint(endpointURL) {
        return minio.BucketLookupDNS
    }
    return minio.BucketLookupAuto
}
```

最后，在吭哧吭哧一顿读代码写代码打包镜像测试后，终于是修复了这个问题并提交了pr。然后我去minio项目下看了下能不能也提个pr，结果发现早有人这么干了：[feat: using virtual hosted style for Tencent Cloud COS](https://github.com/minio/minio-go/pull/2114)。但维护者明确指出不再专门添加后端，而是由用户自行设置，所以并没有被合并。

经典重复造轮子，要是早点搜一下就好了。
