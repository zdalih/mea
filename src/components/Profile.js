import React, {Component} from 'react'
import axios from 'axios'
import MyNavbar from '../components/Navbar'
import Movie from '../components/Movie'
import {Container, Row, Col} from 'reactstrap'
import profImg from '../media/profile.png'
import ScrollArea from 'react-scrollbar'
import ProfileSmall from '../components/ProfileSmall'
import '../css/Profile.css'

const navbarItems = [
    {
        logout: true
    },
    {
        scrollLink: false,
        to: "/profile",
        name: "Profile"
    }
]

export default class Profile extends Component {
    constructor(props) {
        super(props);
        this.state = {
            user: {
                movies: [],
                username: "",
                bio: "",
                followers: [],
                followings: [],
                recommendations: []
            }
        }
    }

    componentDidMount() {
        let authToken = localStorage.getItem('authToken');
        if (authToken) {
            axios.defaults.headers.common['Authorization'] = authToken;
        }
        let url = '/api/profile/';
        if (this.props.match.params.id) {
            url += this.props.match.params.id;
        }
        console.log("Profile calling");
        console.log(url)
        axios.get(url)
        .then((response) => {
            console.log(response);
            let data = response.data;
            this.setState({user: data});
        })
        .catch((error) => {
            console.log(error);
        })
    }

    render() {

        let cover = <div style={{objectFit: "cover", top: "0", bottom: "0", height: "10px", width: "10px", backgroundColor: "black"}}> </div>
        let user = this.state.user;

        return (
            <Container>
                <MyNavbar history={this.props.history} items={navbarItems} search={true} />
                
                <div className="left">
                    <Row>
                        <Col className="my-profile">
                            {/* <p>{user.username}</p> */}
                            <ProfileSmall style={{cursor: "pointer", width: "80%"}} user={user} history={this.props.history} clickable={true}/>
                            {/* <div className="bio">
                                <p>{user.bio}</p>
                            </div> */}
                        </Col>
                    </Row>
                </div>
                
                <div className="right">
                    <h4> Movies </h4>
                    <Row className="profile-row">
                            <Col md="12">
                            {user.movies.map((movie) => {
                                return (
                                    <Movie style={{marginTop: "10px", cursor: "pointer", display: "inline-block"}} movie={movie} history={this.props.history}/>
                                )
                            })}
                            </Col>
                    </Row>  

                    <h4>Followers</h4>
                    <Row className="profile-row">
                            <Col md="12">
                            {user.followers.map((f) => {
                                return (
                                    <ProfileSmall style={{marginTop: "10px", cursor: "pointer", marginLeft: "5px", marginRight: "5px", display: "inline-block"}} user={f} history={this.props.history} clickable={true}/>
                                )
                            })}
                            </Col>
                    </Row>

                    <h4>Recommended</h4>
                    <Row className="profile-row">
                        <Col md="12">
                            {user.recommendations.map((movie) => {
                                return (
                                    <Movie style={{cursor: "pointer", display: "inline-block"}} movie={movie} cover={cover} history={this.props.history}/>
                                )
                            })}
                        </Col>
                    </Row>

                    <h4>Following</h4>
                    <Row className="profile-row">
                        <Col md="12">
                            {user.followings.map((f) => {
                                return (
                                    <ProfileSmall style={{marginTop: "10px", cursor: "pointer", marginLeft: "5px", marginRight: "5px", display: "inline-block"}} user={f} history={this.props.history} clickable={true}/>
                                )
                            })}
                        </Col>
                    </Row>
                </div>
            </Container>
        )
    }
}