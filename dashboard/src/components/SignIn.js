import React, { Component, useState } from 'react';
import Avatar from '@material-ui/core/Avatar';
import Button from '@material-ui/core/Button';
import CssBaseline from '@material-ui/core/CssBaseline';
import TextField from '@material-ui/core/TextField';
import Link from '@material-ui/core/Link';
import Grid from '@material-ui/core/Grid';
import LockOutlinedIcon from '@material-ui/icons/LockOutlined';
import Typography from '@material-ui/core/Typography';
import { makeStyles } from '@material-ui/core/styles';
import Container from '@material-ui/core/Container';
import axios from "axios";

const useStyles = makeStyles((theme) => ({
    paper: {
        marginTop: theme.spacing(8),
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
    },
    avatar: {
        margin: theme.spacing(1),
        backgroundColor: theme.palette.secondary.main,
    },
    form: {
        width: '100%', // Fix IE 11 issue.
        marginTop: theme.spacing(1),
    },
    submit: {
        margin: theme.spacing(3, 0, 2),
    },
}));

export var SignIn = (props) => {
    const classes = useStyles();
    const [uname, setUname] = useState("")
    const [pw, setPw] = useState("")
    const [error, setError] = useState(false)
    const [errorMsg, setErrorMsg] = useState("")

    const handleSingIn = async function (e) {
        e.preventDefault()
        var endpoint = "/user/login?uname="
        endpoint += uname
        endpoint += "&pw="
        endpoint += pw

        try {
            var res = await axios.get(endpoint);

            if (res.status === 200) {
                const status = res.data["status"];
                const token = res.data["auth_token"];
                console.log(token)
                if (status === "success") {
                    props.handleUserToken(token)
                } else {
                    setError(true)
                    setErrorMsg("Login Failed: Username or password is incorrect")
                }
            }
        } catch (error) {
            alert("Error Occured during Sign In");
        }
    }

    return (
        <Container component="main" maxWidth="xs">
            <CssBaseline />
            <div className={classes.paper}>
                <Avatar className={classes.avatar}>
                    <LockOutlinedIcon />
                </Avatar>
                <Typography component="h1" variant="h5">
                    Sign in
                </Typography>
                <form className={classes.form} noValidate>
                    <TextField
                        error={error}
                        helperText={errorMsg}
                        variant="outlined"
                        margin="normal"
                        required
                        fullWidth
                        label="Username"
                        name="uname"
                        autoComplete="uname"
                        autoFocus
                        onChange={(e) => setUname(e.target.value)}
                    />
                    <TextField
                        error={error}
                        helperText={errorMsg}
                        variant="outlined"
                        margin="normal"
                        required
                        fullWidth
                        label="Password"
                        type="password"
                        autoComplete="current-password"
                        onChange={(e) => setPw(e.target.value)}
                    />
                    <Button
                        type="submit"
                        fullWidth
                        variant="contained"
                        color="primary"
                        className={classes.submit}
                        onClick={(e) => handleSingIn(e)}
                    >
                        Sign In
                    </Button>
                    <Grid container>
                        <Grid item>
                            <Link href="#" variant="body2">
                                {"Don't have an account? Sign Up"}
                            </Link>
                        </Grid>
                    </Grid>
                </form>
            </div>
        </Container>
    );
}