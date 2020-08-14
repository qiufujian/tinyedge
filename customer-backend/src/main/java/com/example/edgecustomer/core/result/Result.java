package com.example.edgecustomer.core.result;

import com.alibaba.fastjson.JSON;
import com.fasterxml.jackson.annotation.JsonInclude;

/**
 * 统一API响应结果封装
 *
 * Created by Floki on 2017/9/28.
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
public class Result<T> {

    private static final long serialVersionUID = -6878053406541100993L;
    /**
     * 业务处理的状态代码
     */
    private int code;

    /**
     * 业务处理的状态提示信息
     */
    private String message;

    /**
     * 业务处理的返回状态
     */
    private T data;

    public Result setCode(Code code) {
        this.code = code.getCode();
        this.message = code.getMessage();
        return this;
    }

    public Result setMessage(String message) {
        this.message = message;
        return this;
    }

    public Result setData(T data) {
        this.data = data;
        return this;
    }

    public int getCode() {
        return code;
    }

    public String getMessage() {
        return message;
    }

    public T getData() {
        return data;
    }

    @Override
    public String toString() {
        return JSON.toJSONString(this);
    }
}
