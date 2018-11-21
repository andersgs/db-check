'''
A library of messages using click.secho
'''

import click


def echo_stream(msg, col):
    click.secho(msg, fg=col, err=True)


def info(msg):
    echo_stream(msg, col="blue")


def error(msg):
    echo_stream(msg, col="red")


def warning(msg):
    echo_stream(msg, col="yellow")


def success(msg):
    echo_stream(msg, col="green")
